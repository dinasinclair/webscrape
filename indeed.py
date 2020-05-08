import requests
from bs4 import BeautifulSoup
from selenium import webdriver

# All MLE SEA
ALL_MLE_SEA_URL = 'https://www.indeed.com/q-machine-learning-engineer-l-Seattle,-WA-jobs.html'
# Just Apply-Now Luminex (has generic binary gender, veteran, race extra questions)
APPLY_NOW_LUMINEX_URL = 'https://www.indeed.com/jobs?q=machine+learning+engineer+luminex&l=Seattle%2C+WA'
# Just Apply-Now Technosoft (Has only non-diversity extra questions)
APPLY_NOW_TECHNOSOFT_URL = 'https://www.indeed.com/jobs?q=machine+learning+engineer+technosoft&l=Seattle%2C+WA'
# Convoy Apply On Company Website has pronoun question (on lever)
APPLY_ON_COMPANY_SITE_CONVOY_URL = 'https://www.indeed.com/jobs?q=software+engineer+convoy&l=Seattle%2C+WA'
# greenhouse example
APPLY_ON_COMPANY_SITE_TUSIMPLE_URL = 'https://www.indeed.com/jobs?q=machine+learning+engineer+tusimple&l=Seattle%2C+WA'
# lever second example
APPLY_ON_COMPANY_SITE_OUTREACH_URL = 'https://www.indeed.com/jobs?q=machine+learning+engineer+outreach+knowledge+assets&l=Seattle%2C+WA'
# second greenhouse - the ACLU, so it has cisgender, transgender, non-binary
APPLY_ON_COMPANY_SITE_ACLU = 'https://www.indeed.com/jobs?q=aclu+engineer&l='


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


def get_apply_now_text(chrome_driver):
    # Find apply button for apply-now scenario
    apply_button = chrome_driver.find_element_by_id('indeedApplyButtonContainer')

    # Click on apply button for apply-now
    apply_button.click()
    chrome_driver.implicitly_wait(10)
    iframe = chrome_driver.find_element_by_xpath("//iframe[@title='No content']")
    chrome_driver.switch_to.frame(iframe)
    chrome_driver.implicitly_wait(10)
    iframe_apply = chrome_driver.find_element_by_xpath("//iframe[@title='Apply Now']")
    chrome_driver.switch_to.frame(iframe_apply)
    chrome_driver.implicitly_wait(10)
    return chrome_driver.page_source


def get_company_site_text(chrome_driver):
    # Click on apply button for on company site
    link_to_site = chrome_driver.find_element_by_xpath('//a[text()="Apply On Company Site"]')
    chrome_driver.get(link_to_site.get_attribute('href'))
    print("current url: ", driver.current_url)

    # Process all lever jobs
    if chrome_driver.current_url.startswith("https://jobs.lever.co"):
        print("This is a jobs.lever application")
        # First page is description for lever forms, second page is app questions
        link_to_app = chrome_driver.find_element_by_xpath('//a[text()="Apply for this job"]')
        chrome_driver.get(link_to_app.get_attribute('href'))
        return chrome_driver.page_source
    # Process all greenhouse jobs
    if chrome_driver.current_url.startswith("https://boards.greenhouse.io/"):
        print("This is a boards.greenhouse application")
        # greenhouse jobs put their info on the initial page, no click through needed!
        return chrome_driver.page_source
    else:
        return "testtesttest"


def html_to_stats(html_text):
    # Get BS from page source, convert to lowercase text blob
    app_soup = BeautifulSoup(html_text, "html.parser")
    app_text = app_soup.get_text("\n", strip=True).lower()

    # print text and stats
    print("APP TEXT: \n", app_text)
    for key_word in ["gender",
                     "pronoun",
                     "female",
                     "veteran",
                     "race",
                     "nonbinary",
                     "non-binary",
                     "cisgender",
                     "transgender",
                     "diversity"]:
        if app_text.count(key_word) > 0:
            print(
                "The word {} appears in the application {} times".format(key_word, app_text.count(key_word)))


def get_all_job_links(soup):
    # Collect all job page links from search results
    job_links = []
    for link in soup.findAll('a', class_="jobtitle turnstileLink"):
        job_links.append(link)

    return job_links


def process_job_url(chrome_driver, job_page_url):
    driver.get(job_page_url)
    # Check if this is an apply-now job
    is_apply_now = len(chrome_driver.find_elements_by_id('indeedApplyButtonContainer')) == 1

    if is_apply_now:
        print("This is an apply now job!")
        app_text = get_apply_now_text(chrome_driver)


    else:
        print("This is an external application!")
        app_text = get_company_site_text(chrome_driver)

    html_to_stats(app_text)


if __name__ == "__main__":
    search_url = APPLY_ON_COMPANY_SITE_ACLU

    # Connect to the search result URL
    response = requests.get(search_url)

    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")

    # Grabbing first job link as an example
    job_links = get_all_job_links(soup)
    example_job = job_links[0]

    # Get and connect to the job page URL
    job_url = 'http://indeed.com/' + example_job['href']
    print("job page url: ", job_url)
    driver = webdriver.Chrome()

    process_job_url(driver, job_url)



    print("Done!! :D")

    # driver.close()
