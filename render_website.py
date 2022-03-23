import json
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from pathlib import Path


def rebuild():
    with open('result.json', 'r') as file:
        book_data = json.load(file)
    books_in_column = 20
    distributed_data = list(chunked(book_data, books_in_column))
    env = Environment(loader=FileSystemLoader('.'),
                      autoescape=select_autoescape(['html', 'xml'])
                      )
    for i, books in enumerate(distributed_data, 1):
        template = env.get_template('template.html')
        column_data = list(chunked(books, books_in_column//2))
        number_of_page = len(distributed_data)
        rendered_page = template.render(column_data=column_data,
                                        number_of_page=number_of_page,
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
