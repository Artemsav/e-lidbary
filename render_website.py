from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

with open('.json', 'r') as file:
    data = json.load(file)
print(data)
