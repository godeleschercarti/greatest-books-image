import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

names_list = []
authors_list = []
images_list = []
urls_list = []

for i in range(1, 5):
    url = f"https://thegreatestbooks.org/page/{i}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    names = [x.find_all("a")[0].contents[0] for x in soup.find_all("h4")[0:25]]

    authors = []
    for x in soup.find_all("h4")[0:25]:
        if len(x.find_all("a")) > 1: author = x.find_all("a")[1].contents[0]
        else: author = "Unknown"
        authors.append(author)

    images = [x['src'] for x in soup.find_all("img")[1:26]]
    
    names_list = names_list + names
    authors_list = authors_list + authors
    images_list = images_list + images

    time.sleep(3)
    print(f"Downloaded to book #{i*25}.")

for i in range(len(images_list)):
    image_url = images_list[i]
    name = names_list[i].lower()
    
    for word, initial in {".": "", ",": "", "'": "", "!": "", " ": "-"}.items():
        name = name.replace(word.lower(), initial)
    if name[:4] == "the-": name = name[4:]
    name = name + ".jpg"
    urls_list.append(name)
        
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        with open(f"images/{name}", "wb") as file:
            file.write(response.content)
        print(f"Downloaded image {name} successfully!")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")
    time.sleep(2)

pd.DataFrame({"name": names_list, "author": authors_list, "image": urls_list}).to_csv('details.csv')