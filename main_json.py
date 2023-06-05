import time

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os.path
import yaml
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

parent_url = 'https://www.goodreads.com'

#Create config.yaml with:
# path (where to save files)
# url profile with books read

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

filepath = data['save_path_local']
url = data['url_goodreads']

list_books = []

def retrieve_book_info(book_url):
    main_url = 'https://goodreads.com'
    final_url = main_url + book_url
    response = requests.get(final_url, headers=headers)
    time.sleep(1)
    soup = BeautifulSoup(response.content, "html.parser")
    img_link = soup.find('img', {'class': 'ResponsiveImage'})['src']
    description = soup.find('span', {'class': 'Formatted'}).text
    
    return img_link, description


def retrieve_book_info_js(book_url):

    try:

        main_url = 'https://goodreads.com'
        final_url = main_url + book_url

        WINDOW_SIZE = "1920,1080"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)

        # chrome_options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])")
        driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
        driver.get(final_url)

        wait = WebDriverWait(driver, 20)  # 10 seconds maximum wait time
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img.ResponsiveImage")))

        html = driver.page_source


        soup = BeautifulSoup(html, "html.parser")
        img_link = soup.find('img', {'class': 'ResponsiveImage'})['src']
        description = soup.find('span', {'class': 'Formatted'}).text
        return img_link, description

    except:
        return None, None




headers = {'User-agent': 'Mozilla/5.0'}

for i in range(1, 4):
    url = url.replace('=1&', '=' + str(i) + '&')


    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    books = soup.select('img[id*="cover_review"]')
    dates = soup.find_all("span", {'class': "date_read_value"})
    authors = soup.find_all("td", {'class': "field author"})
    counter = 1

    #workaround timestamp sorting in Jekyll
    days_substract = 10_000


    for book in books:
        try:
            title = book['alt']
            cover = book['src']
            book_url = book.findNext('a')['href']
            img_link, description = retrieve_book_info_js(book_url)
            if img_link is None:
                img_link, description = retrieve_book_info_js(book_url)
            author = book.findNext('td', {'class': "field author"}).findNext('a').text
            order = counter
            counter = counter+1
            date = datetime.now() - timedelta(days_substract-counter)
            link = book.findParent().findParent().find('a')['href']
            formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
            formatted_date = formatted_date+' -0400'
            merged_link = parent_url + link

            dict_book = {'title': title, "cover": img_link, 'link': merged_link, 'author': author, 'description': description}
            if dict_book not in list_books:
                list_books.append(dict_book)
        except:
            print('error with book: ' + title)

dict_books = {'books': list_books}


full_name = os.path.join(filepath, "books" + ".json")


with open(full_name, 'w', encoding='utf-8') as file:
    json.dump(dict_books, file)

    file.close()

