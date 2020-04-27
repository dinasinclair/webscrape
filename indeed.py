import requests
import urllib.request
import time
from bs4 import BeautifulSoup

# Set the URL you want to webscrape from
url = 'https://www.indeed.com/jobs?q=machine+learning+engineer&l=Seattle%2C+WA'

# Connect to the URL
response = requests.get(url)

# Parse HTML and save to BeautifulSoup object
soup = BeautifulSoup(response.text, "html.parser")
job_links = []

for tag in soup.findAll('a', class_="jobtitle turnstileLink"):
    print(tag["title"])
    # print(tag["href"])
    job_links.append(tag)
print (len(job_links))




# # # To download the whole data set, let's do a for loop through all a tags
# for tag in soup.findAll('a'):  # 'a' tags are for links
#     print(tag)
#     if tag.has_attr('href') and tag['href'].startswith("/q-"):
#         job_links.append(tag)
#
# # for tag in job_links:
# #     print(tag['href'])
# print (len(job_links))
#     # print (tag['href'])
# #    try:
# #        link = tag['href']
# #    except:
# #        print("no href in ", tag)
# #    if 'data/nyct/turnstile' in link:
# #        print("link: ", link)
# #        download_url = 'http://web.mta.info/developers/' + link
# #        urllib.request.urlretrieve(download_url, './' + link[link.find('/turnstile_') + 1:])
# #        time.sleep(1)  # pause the code for a sec