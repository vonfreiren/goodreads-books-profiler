from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os.path
import yaml
import json
from selenium import webdriver
import time

parent_url = 'https://www.goodreads.com'

#Create config.yaml with:
# path (where to save files)
# url profile with books read

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

filepath = data['save_path_local']
url = data['url_goodreads']

WINDOW_SIZE = "1920,1080"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

# chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])")
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
driver.execute_script("window.scrollBy(0, 5000)")


time.sleep(0.2)

html = driver.page_source


headers = {'User-agent': 'Mozilla/5.0'}
soup = BeautifulSoup(html, "html.parser")
books = soup.select('img[id*="cover_review"]')
dates = soup.find_all("span", {'class': "date_read_value"})
authors = soup.find_all("td", {'class': "field author"})
counter = 1

#workaround timestamp sorting in Jekyll
days_substract = 10_000

list_books = []

for book in books:
    title = book['alt']
    cover = book['src']
    author = book.findNext('td', {'class': "field author"}).findNext('a').text
    order = counter
    counter = counter+1
    date = datetime.now() - timedelta(days_substract-counter)
    link = book.findParent().findParent().find('a')['href']
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    formatted_date = formatted_date+' -0400'
    merged_link = parent_url + link

    dict_book = {'title': title, "cover": cover, 'order': order, 'date': formatted_date, 'link': merged_link, 'author': author}
    list_books.append(dict_book)

dict_books = {'books': list_books}


full_name = os.path.join(filepath, "books" + ".json")


with open(full_name, 'w', encoding='utf-8') as file:
    json.dump(dict_books, file)

    file.close()

