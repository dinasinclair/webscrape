import requests
from bs4 import BeautifulSoup
from selenium import webdriver


def print_all_iframes(chrome_driver):
    print("all iframes: ")
    iframes = chrome_driver.find_elements_by_xpath("//iframe")
    print("found {} frames".format(len(iframes)))
    for frame in iframes:
        print(frame)
        print(frame.get_attribute('id'))
        print(frame.get_attribute('title'))


def print_all_ids_avail(chrome_driver):
    print("all ids:")
    ids = chrome_driver.find_elements_by_xpath('//*[@id]')
    for ii in ids:
        # if 'apply' in ii.get_attribute('id'):
        print(ii.get_attribute('id'))


# Set the URL you want to webscrape from
# All MLE SEA
# url = 'https://www.indeed.com/q-machine-learning-engineer-l-Seattle,-WA-jobs.html'
# Just Apply-Now Luminex (has generic binary gender, veteran, race extra questions)
# url = 'https://www.indeed.com/jobs?q=machine+learning+engineer+luminex&l=Seattle%2C+WA'
# Just Apply-Now Technosoft (Has only non-diversity extra questions)
# url = 'https://www.indeed.com/jobs?q=machine+learning+engineer+technosoft&l=Seattle%2C+WA'
# Convoy Apply On Company Website has pronoun question
url = 'https://www.indeed.com/jobs?q=software+engineer+convoy&l=Seattle%2C+WA'

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
# print(driver.page_source)

def get_app_generic():
    # Find apply button for apply-now scenario
    apply_button = driver.find_element_by_id('indeedApplyButtonContainer')

    # Click on apply button for apply-now
    apply_button.click()
    driver.implicitly_wait(10)
    iframe = driver.find_element_by_xpath("//iframe[@title='No content']")
    driver.switch_to.frame(iframe)
    driver.implicitly_wait(10)
    iframe_apply = driver.find_element_by_xpath("//iframe[@title='Apply Now']")
    driver.switch_to.frame(iframe_apply)
    driver.implicitly_wait(10)

def get_company_site():
    # Click on apply button for on company site
    link_to_site = driver.find_element_by_xpath('//a[text()="Apply On Company Site"]')
    driver.get(link_to_site.get_attribute('href'))


app_soup = BeautifulSoup(driver.page_source, "html.parser")

app_text = app_soup.get_text("\n", strip=True).lower()

print("APP TEXT: \n", app_text)

for key_word in ["gender", "pronoun", "female", "veteran", "race", "diversity"]:
    print(
        "The word {} appears in the application {} times".format(key_word, app_text.count(key_word)))

print("Done!! :D")

driver.close()
