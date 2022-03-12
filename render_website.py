import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def rebuild():
    with open('result.json', 'r') as file:
        data = json.load(file)
    env = Environment(loader=FileSystemLoader('.'),
                      autoescape=select_autoescape(['html', 'xml'])
                      )
    template = env.get_template('template.html')
    rendered_page = template.render(
      data=data,
    )
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    rebuild()
    server = Server()
    server.watch('template.html', rebuild)
    server.serve(root='.')
