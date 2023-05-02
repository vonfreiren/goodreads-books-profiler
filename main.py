from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import os.path
import yaml

parent_url = 'https://www.goodreads.com'

#Create config.yaml with:
# path (where to save files)
# url profile with books read

with open('config.yaml') as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

filepath = data['save_path_local']
url = data['url_goodreads']



headers = {'User-agent': 'Mozilla/5.0'}
soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
books = soup.select('img[id*="cover_review"]')
dates = soup.find_all("span", {'class': "date_read_value"})
counter = 1

#workaround timestamp sorting in Jekyll
days_substract = 10_000

for book in books:
    title = book['alt']
    cover = book['src']
    order = counter
    counter = counter+1
    date = datetime.now() - timedelta(days_substract-counter)
    link = book.findParent().findParent().find('a')['href']
    formatted_date = date.strftime('%Y-%m-%d %H:%M:%S')
    formatted_date = formatted_date+' -0400'
    merged_link = parent_url + link


    title_quotes = f'"{title}"'
    full_name = os.path.join(filepath, title + ".md")

    with open(full_name, 'w', encoding='utf-8') as file:
        file.write("---")
        file.write('\n')
        file.write("title: "+title_quotes)
        file.write('\n')
        file.write("background: "+cover)
        file.write('\n')
        file.write("description: "+merged_link)
        file.write('\n')
        file.write("date: "+formatted_date)
        file.write('\n')
        file.write("---")
        file.write('\n')

        file.close()

