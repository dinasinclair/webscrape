import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# Set the URL you want to webscrape from
# url = 'https://www.indeed.com/q-machine-learning-engineer-l-Seattle,-WA-jobs.html'
url = 'https://www.indeed.com/jobs?q=machine+learning+engineer+luminex&l=Seattle%2C+WA'

# Connect to the search result URL
response = requests.get(url)

# Parse HTML and save to BeautifulSoup object
soup = BeautifulSoup(response.text, "html.parser")

# Collect all job page links from search results
job_links = []
titles_found = []
for tag in soup.findAll('a', class_="jobtitle turnstileLink"):
    title = tag["title"]
    titles_found.append(title)
    job_links.append(tag)

# Grabbing first job link as an example
tag = job_links[0]

# Get and connect to the job page URL
job_page_url = 'http://indeed.com/' + tag['href']
print("job page url: ", job_page_url)
driver = webdriver.Chrome()
driver.get(job_page_url)

# Find apply button
apply_button = driver.find_element_by_id('indeedApplyButtonContainer')

# Click on apply button
apply_button.click()
driver.implicitly_wait(10)
iframe = driver.find_element_by_xpath("//iframe[@title='No content']")
driver.switch_to.frame(iframe)
driver.implicitly_wait(10)
iframe_apply = driver.find_element_by_xpath("//iframe[@title='Apply Now']")
driver.switch_to.frame(iframe_apply)
driver.implicitly_wait(10)
print(driver.page_source)

for key_word in ["gender", "pronoun", "female", "veteran", "race", "diversity"]:
    print(
        "The word {} appears in the application {} times".format(key_word, driver.page_source.lower().count(key_word)))

print("Done!! :D")

driver.close()


def print_all_iframes(chrome_driver):
    iframes = chrome_driver.find_elements_by_xpath("//iframe")
    print(len(iframes))
    for frame in iframes:
        print("\nnew frame: ")
        print(frame.get_attribute('id'))
        print(frame.get_attribute('title'))
