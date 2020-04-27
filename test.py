# From https://towardsdatascience.com/how-to-web-scrape-with-python-in-4-minutes-bc49186a8460
import requests
import urllib.request
import time
from bs4 import BeautifulSoup

# Set the URL you want to webscrape from
url = 'http://web.mta.info/developers/turnstile.html'

# Connect to the URL
response = requests.get(url)

# Parse HTML and save to BeautifulSoup object¶
soup = BeautifulSoup(response.text, "html.parser")

# To download the whole data set, let's do a for loop through all a tags
for tag in soup.findAll('a'):  # 'a' tags are for links
   try:
       link = tag['href']
   except:
       print("no href in ", tag)
   if 'data/nyct/turnstile' in link:
       print("link: ", link)
       download_url = 'http://web.mta.info/developers/' + link
       urllib.request.urlretrieve(download_url, './' + link[link.find('/turnstile_') + 1:])
       time.sleep(1)  # pause the code for a sec