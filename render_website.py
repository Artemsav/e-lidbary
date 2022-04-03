import json
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from pathlib import Path


def rebuild():
    with open('result.json', 'r') as file:
        books = json.load(file)
    books_on_page = 20
    chunked_books = list(chunked(books, books_on_page))
    env = Environment(loader=FileSystemLoader('.'),
                      autoescape=select_autoescape(['html', 'xml'])
                      )
    for i, books in enumerate(chunked_books, 1):
        template = env.get_template('template.html')
        books_columns = list(chunked(books, books_on_page//2))
        number_of_pages = len(chunked_books)
        rendered_page = template.render(books_columns=books_columns,
                                        number_of_page=number_of_pages,
                                        page=i
                                        )
        folder_dest = './pages/'
        pages_path = f'{folder_dest}index{i}.html'
        Path(folder_dest).mkdir(exist_ok=True)
        with open(pages_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


if __name__ == '__main__':
    rebuild()
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')
