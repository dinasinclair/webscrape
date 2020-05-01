import requests
from bs4 import BeautifulSoup

# Set the URL you want to webscrape from
url = 'https://www.indeed.com/q-machine-learning-engineer-l-Seattle,-WA-jobs.html'

# Connect to the URL
response = requests.get(url)

print(response.text)