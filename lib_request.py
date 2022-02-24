from urllib.parse import urljoin
from urllib.parse import urlsplit
import requests
from pathlib import Path
import pathlib
import os
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
import argparse
from tqdm import tqdm


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        named_path: Путь до файла, куда сохранён текст.
    """
    path = os.path.join(pathlib.Path().resolve(), folder)
    Path(path).mkdir(parents=True, exist_ok=True)
    named_path = '{path}{filename}.txt'.format(path=path, filename=sanitize_filename(filename))
    response = requests.get(url)
    response.raise_for_status()
    with open(named_path, 'w', encoding="utf-8") as file:
        file.write(response.text)


def download_image(url, filename, folder='images/'):
    """Функция для скачивания картинок.
    Args:
        url (str): Cсылка на картинку, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        named_path: Путь до файла, куда сохранёно изображение.
    """
    path = os.path.join(pathlib.Path().resolve(), folder)
    Path(path).mkdir(parents=True, exist_ok=True)
    named_path = '{path}{filename}'.format(path=path, filename=sanitize_filename(filename))
    response = requests.get(url)
    response.raise_for_status()
    with open(named_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    """Функция для получения всех данных по книге
    """
    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.select_one('h1').get_text().split('::')
    title, author = title_text
    if soup.select_one('.bookimage'):
        picture_selector = '.bookimage img'
        picture_link = soup.select_one(picture_selector)['src']
    else:
        picture_link = None
    parse_genre = soup.select('span.d_book a')
    genres = []
    for genre in parse_genre:
        genres.append(genre.get_text())
    parsed_table = soup.select('table.d_book a')
    txt_link = None
    for tag_a in parsed_table:
        if 'txt' in tag_a['href']:
            txt_link = urljoin(response.url, tag_a['href'])
    parse_comments = soup.select('.texts span')
    comments = []
    for comment in parse_comments:
        comments.append(comment.get_text())
    return {'title': title.strip(),
            'author': author.strip(),
            'picture_link': urljoin(response.url, picture_link),
            'txt_link': txt_link,
            'comments': comments,
            'genres': genres,
            }


def parse_user_input():
    """Функция для парсинга пользовательского ввода
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', help='Start id of book to be parsed', type=int)
    parser.add_argument('end_id', help='End id of book to be parsed', type=int)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main_url = 'https://tululu.org/'
    user_input = parse_user_input()
    for book_id in tqdm(range(user_input.start_id, user_input.end_id+1),
                        ):
        book_url = urljoin(main_url, ('b{book_id}/'.format(book_id=book_id)))
        response = requests.get(book_url)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            book_data = parse_book_page(response)
        except requests.exceptions.HTTPError:
            pass
        txt_link = book_data.get('txt_link')
        image_link = book_data.get('picture_link')
        if txt_link:
            title_text = book_data.get('title')
            filename = '{book_id}. {title_text}'.format(book_id=str(book_id), title_text=title_text)
            download_txt(url=txt_link, filename=filename)
        if image_link:
            image_link = book_data.get('picture_link')
            image_name = urlsplit(image_link)[2].split('/')[-1]
            download_image(url=urljoin(main_url, image_link), filename=image_name)
