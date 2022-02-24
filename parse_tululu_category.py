import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlsplit
from lib_request import download_txt, download_image, parse_book_page, check_for_redirect
import json
from pathvalidate import sanitize_filename

if __name__ == '__main__':
    main_url = 'https://tululu.org/'
    url = 'http://tululu.org/l55/'
    books_data = []
    books_path = 'books/'
    images_path = 'images/'
    for page_id in range(1, 5):
        book_url = urljoin(url, ('{page_id}/'.format(page_id=page_id)))
        response = requests.get(book_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        parsed_tables = soup.select('table.d_book .bookimage a')
        for tag_a in parsed_tables:
            if 'b' in tag_a['href']:
                book_link = urljoin(response.url, tag_a['href'])
                try:
                    book_response = requests.get(book_link)
                    book_response.raise_for_status()
                    check_for_redirect(book_response)
                    book_data = parse_book_page(book_response)
                except requests.exceptions.HTTPError:
                    pass
                txt_link = book_data.get('txt_link')
                image_link = book_data.get('picture_link')
                if txt_link:
                    split_book_url = book_link.split('b')
                    _, book_id = split_book_url
                    title_text = book_data.get('title')
                    filename = '{book_id}. {title_text}'.format(book_id=book_id, title_text=title_text)
                    download_txt(url=txt_link, filename=filename)
                    if image_link:
                        image_link = book_data.get('picture_link')
                        image_name = urlsplit(image_link)[2].split('/')[-1]
                        print(image_name)
                        download_image(url=urljoin(main_url, image_link), filename=image_name)
                    book_inf = {'title': title_text,
                                'author': book_data.get('author'),
                                'img_src': '{images_path}{image_name}'.format(images_path=images_path , image_name=image_name),
                                'book_path': '{books_path}{filename}.txt'.format(books_path=books_path, filename=sanitize_filename(filename)),
                                'comments': book_data.get('comments'),
                                'genres': book_data.get('genres'),
                                }
                    books_data.append(book_inf)
    jjson = json.dumps(books_data, indent=6, ensure_ascii=False)
    with open(".json", "w") as book_json:
        book_json.write(jjson)
