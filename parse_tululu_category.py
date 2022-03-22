import argparse
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from lib_request import (check_for_redirect, download_image, download_txt,
                         parse_book_page)


def select_last_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    all_pages = soup.select('a.npage')
    last_page = all_pages[-1].get_text()
    return last_page


def parse_user_input():
    """Функция для парсинга пользовательского ввода
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_page',
                        help='Start page of book to be parsed',
                        type=int, default=1,
                        )
    parser.add_argument('-e', '--end_page',
                        help='End page of book to be parsed',
                        type=int,
                        )
    parser.add_argument('-df', '--dest_folder',
                        help='Folder for parsing book and images',
                        action='store', default='.'
                        )
    parser.add_argument('-si', '--skip_imgs',
                        action='store_true',
                        help='Skip images parsing',
                        )
    parser.add_argument('-st', '--skip_txt',
                        action='store_true',
                        help='Skip .txt parsing',
                        )
    parser.add_argument('-jp', '--json_path',
                        help='Json path',
                        )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main_url = 'https://tululu.org/'
    url = 'http://tululu.org/l55/'
    user_input = parse_user_input()
    books_data = []
    dest_folder = user_input.dest_folder
    books_path = f'{dest_folder}/books/'
    images_path = f'{dest_folder}/images/'
    if not user_input.end_page:
        user_input.end_page = int(select_last_page(url))
    for page_id in range(user_input.start_page, user_input.end_page):
        book_url = urljoin(url, str(page_id))
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        books_link = soup.select('table.d_book .bookimage a[href*="b"]')
        for link in books_link:
            book_link = urljoin(response.url, link['href'])
            try:
                book_response = requests.get(book_link)
                book_response.raise_for_status()
                check_for_redirect(book_response)
                book_data = parse_book_page(book_response)
            except requests.exceptions.HTTPError:
                pass
            txt_link = book_data.get('txt_link')
            image_link = book_data.get('picture_link')
            book_data['book_path'] = book_data.pop('txt_link')
            if txt_link:
                splitted_book_url = book_link.split('b')
                _, book_id = splitted_book_url
                title_text = book_data.get('title')
                filename = f'{book_id}. {title_text}.txt'
                book_data['book_path'] = f'{books_path}{sanitize_filename(filename)}'
                if not user_input.skip_txt:
                    download_txt(url=txt_link, filename=filename,
                                 folder=books_path,
                                 )
            book_data['img_src'] = book_data.pop('picture_link')
            if image_link:
                image_name = urlsplit(image_link)[2].split('/')[-1]
                book_data['img_src'] = f'{images_path}{image_name}'
                if not user_input.skip_imgs:
                    download_image(url=urljoin(main_url, image_link),
                                   filename=image_name,
                                   folder=images_path,
                                   )
            books_data.append(book_data)
    book_json_data = json.dumps(books_data, indent=6, ensure_ascii=False)
    json_path_name = f'{user_input.json_path or user_input.dest_folder}'
    json_path = f'{user_input.json_path or user_input.dest_folder}/result.json'
    Path(json_path_name).mkdir(exist_ok=True)
    with open(json_path, 'w') as book_json:
        book_json.write(book_json_data)
