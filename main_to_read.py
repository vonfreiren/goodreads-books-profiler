from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os.path
import yaml
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import json


url = 'https://www.goodreads.com/review/list/136789999-javier-freire-alvarez?page=1&per_page=30&shelf=to-read&utf8=%E2%9C%93'

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

save_path_books_to_read = data['save_path_local']

list_books_to_read = []

parent_url = 'https://www.goodreads.com'


def retrieve_book_info(book_url):
    main_url = 'https://goodreads.com'
    final_url = book_url
    soup = BeautifulSoup(requests.get(final_url, headers=headers).content, "html.parser")
    img_link = soup.find('img', {'class': 'ResponsiveImage'})['src']
    description = soup.find('span', {'class': 'Formatted'}).text

    return img_link, description


for i in range(1, 10):
    url = 'https://www.goodreads.com/review/list/136789999-javier-freire-alvarez?page={0}&per_page=30&shelf=to-read&utf8=%E2%9C%93'.format(i)



    headers = {'User-agent': 'Mozilla/5.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    books = soup.select('img[id*="cover_review"]')
    dates = soup.find_all("span", {'class': "date_read_value"})
    authors = soup.find_all('td', class_='field author')
    list_authors = []
    for author in authors:
        list_authors.append(author.find('a').text)
    counter = 1
    list_urls = []
    for book in books:
        url = book.findParent().findParent().find('a')['href']
        url = parent_url + url
        list_urls.append(url)

    books = [books['alt'] for books in books]
    #workaround timestamp sorting in Jekyll

    for book, author, url in zip(books, list_authors, list_urls):
        try:
            img_link, description = retrieve_book_info(url)
            dict_book = {'title': book, "cover": img_link, 'link': url, 'author': author, 'description': description}
            list_books_to_read.append(dict_book)

        except:
            pass


    dict_books = {'books': list_books_to_read}


    full_name = os.path.join(save_path_books_to_read, "books_to_read" + ".json")

    with open(full_name, 'w', encoding='utf-8') as file:
        json.dump(dict_books, file)

        file.close()

df_books = pd.DataFrame(list_books_to_read)
df_books['Title'] = '<a href="'+df_books['URL']+'">'+df_books['Title']+'</a>'
df_books = df_books.drop(columns=['URL'])

df_books.to_html(save_path_books_to_read, index=False, classes='table-responsive table-bordered', table_id='table_wishlist_books',
                    border=0, escape=False, justify='center', col_space=100, na_rep='N/A', formatters={'Title': lambda x: x})





