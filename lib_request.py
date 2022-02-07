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
        str: Путь до файла, куда сохранён текст.
    """
    path = os.path.join(pathlib.Path().resolve(), folder)
    Path(path).mkdir(exist_ok=True)
    named_path = '{path}{filename}.txt'.format(path=path,
                                               filename=sanitize_filename(filename),
                                               )
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
        str: Путь до файла, куда сохранён текст.
    """
    path = os.path.join(pathlib.Path().resolve(), folder)
    Path(path).mkdir(exist_ok=True)
    named_path = '{path}{filename}'.format(path=path,
                                           filename=sanitize_filename(filename),
                                           )
    response = requests.get(url)
    response.raise_for_status()
    with open(named_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    """Функция для получения всех данных по книге
    """
    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.find('h1').text.split('::')
    title, author = title_text
    if soup.find(class_='bookimage'):
        picture_link = soup.find(class_='bookimage').find('img')['src']
    else:
        picture_link = None
    raw_parse_genre = soup.find('span', class_='d_book').text.split(':')
    _, genre = raw_parse_genre
    find_table_with_links = soup.find('table', class_='d_book')
    txt_link = None
    for a in find_table_with_links.find_all('a'):
        if 'txt' in a['href']:
            txt_link = urljoin(response.url,
                               a['href'],
                               )
    return {'title': title.strip(),
            'author': author.strip(),
            'picture_link': urljoin(response.url, picture_link),
            'genre': genre.strip().strip('.'),
            'txt_link': txt_link,
            }


def parse_user_input():
    """Функция для парсинга пользовательского ввода
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', help='Start id of book to be parsed',
                        type=int,
                        )
    parser.add_argument('end_id', help='End id of book to be parsed', type=int)
    args = parser.parse_args()
    if args.start_id and args.end_id:
        index_range = {'start_id': args.start_id, 'end_id': args.end_id+1}
        return index_range


if __name__ == '__main__':
    main_url = 'https://tululu.org/'
    user_input = parse_user_input()
    for book_id in tqdm(range(user_input.get('start_id'),
                              user_input.get('end_id'),
                              ),
                        ):
        book_url = urljoin(main_url, ('b{book_id}/'.format(book_id=book_id)))
        response = requests.get(book_url)
        try:
            response.raise_for_status()
            check_for_redirect(response)
            book_data = parse_book_page(response)
        except requests.exceptions.HTTPError:
            pass
        soup = BeautifulSoup(response.text, 'lxml')
        find_table_with_links = soup.find('table', class_='d_book')
        txt_link = book_data.get('txt_link')
        image_link = book_data.get('picture_link')
        if txt_link:
            title_text = book_data.get('title')
            filename = '{book_id}. {title_text}'.format(book_id=str(book_id),
                                                        title_text=title_text,
                                                        )
            download_txt(url=txt_link, filename=filename)
        if image_link:
            image_link = book_data.get('picture_link')
            image_name = urlsplit(image_link)[2].split('/')[-1]
            download_image(url=urljoin(main_url, image_link),
                           filename=image_name,
                           )
