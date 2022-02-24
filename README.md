# E-library

## Project description

Scripts allow you to download books from electronic library from this [address](https://tululu.org/). Basically, there are two scripts in the repository.

### lib_request script
To run the first one you shall use the following command:

```bash
python lib_request.py 1 10
```
Where the numbers ```1 10``` it is ```id``` of the books on [electronic library](https://tululu.org/). Typical address of the page of the book is ```https://tululu.org/b20/```
When the scripts creates two folders ```books``` with .txt files with book-text and ```images``` with book cover picture.

### parse_tululu_category script
Second one has additional functionality via following optional arguments:
``--start_page`` and ```--end_page``` - They control from which to which page to download.
```--dest_folder``` - path to the directory with parsing results: pictures, books, JSON.
```--skip_imgs``` - do not download images
```--skip_txt``` - do not download books
```--json_path``` — specify your path to *.json file with results
To run the second one you shall use the following command:

```bash
python parse_tululu_category --start_page 700 --end_page 701 --dest_folder dest_folder --skip_txt --json_path json
```
All arguments are optional. This command will download all books from the pages ```700``` to ```701``` to folder ```dest_folder``` without ```.txt``` files. Data about downloaded books will be stored in folder ```json```

## Instalation

Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:

```bash
pip install -r requirements.txt
```


## Project Goals


The code is written for educational purposes on online-course for web-developers [Devman](https://dvmn.org)
