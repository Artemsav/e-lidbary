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
    else:
        pass


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
    path_with_name = '{path}{filename}.txt'.format(path=path,
                                                   filename=sanitize_filename(filename),
                                                   )
    response = requests.get(url)
    response.raise_for_status()
    with open(path_with_name, 'w', encoding="utf-8") as file:
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
    path_with_name = '{path}{filename}'.format(path=path,
                                               filename=sanitize_filename(filename),
                                               )
    response = requests.get(url)
    response.raise_for_status()
    with open(path_with_name, 'wb') as file:
        file.write(response.content)


def parse_book_page(response):
    """Функция для получения всех данных по книге
    """
    soup = BeautifulSoup(response.text, 'lxml')
    title_text = soup.find('h1').text.split('::')
    if soup.find(class_='bookimage'):
        picture_link = soup.find(class_='bookimage').find('img')['src']
    else:
        picture_link = None
    raw_parse_janr = soup.find('span', class_='d_book').text
    janr_in_list = raw_parse_janr.split(':')
    return {'Title': title_text[0].strip(),
            'Author': title_text[1].strip(),
            'link_on_picture': urljoin(response.url, picture_link),
            'Janr': janr_in_list[1].strip().split(',')[0].strip().strip('.')
            }


def parser():
    """Функция для парсинга пользовательского ввода
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', help='Start id of book to be parsed',
                        type=int,
                        )
    parser.add_argument('end_id', help='End id of book to be parsed', type=int)
    try:
        args = parser.parse_args()
        if args.start_id and args.end_id:
            index_range = {'start_id': args.start_id, 'end_id': args.end_id+1}
            return index_range
    except SystemExit:
        print('Invalid input')


if __name__ == '__main__':
    main_url = 'https://tululu.org/'
    user_input = parser()
    for id in tqdm(range(user_input.get('start_id'),
                         user_input.get('end_id'),
                         ),
                   ):
        url_for_book = urljoin(main_url, ('b{id}/'.format(id=id)))
        response = requests.get(url_for_book)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            book_data = parse_book_page(response)
        except requests.exceptions.HTTPError:
            pass
        soup = BeautifulSoup(response.text, 'lxml')
        find_table_with_links = soup.find('table', class_='d_book')
        if find_table_with_links:
            try:
                link_on_txt = urljoin(response.url,
                                      find_table_with_links.find_all('a')[8]['href'],
                                      )
                title_text = book_data.get('Title')
                filename = '{id}. {title_text}'.format(id=str(id),
                                                       title_text=title_text,
                                                       )
                download_txt(url=link_on_txt, filename=filename)
            except IndexError:
                pass
            if soup.find(class_='bookimage'):
                image_link = book_data.get('link_on_picture')
                image_name = urlsplit(image_link)[2].split('/')[-1]
                download_image(url=urljoin(main_url, image_link),
                               filename=image_name,
                               )
