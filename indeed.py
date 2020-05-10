import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

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
# another lever non-binary example
APPLY_NB = 'https://jobs.lever.co/innovateschools/c142ef0c-c426-4c8d-b06c-eb672075cc98/apply'


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
    chrome_driver.implicitly_wait(2)
    iframe = chrome_driver.find_element_by_xpath("//iframe[@title='No content']")
    chrome_driver.switch_to.frame(iframe)
    chrome_driver.implicitly_wait(2)
    iframe_apply = chrome_driver.find_element_by_xpath("//iframe[@title='Apply Now']")
    chrome_driver.switch_to.frame(iframe_apply)
    chrome_driver.implicitly_wait(2)
    return chrome_driver.page_source


def get_company_site_text(chrome_driver):
    # Click on apply button for on company site
    link_to_site = chrome_driver.find_element_by_xpath('//a[text()="Apply On Company Site"]')
    chrome_driver.get(link_to_site.get_attribute('href'))
    print("company site url: ", chrome_driver.current_url)

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
    # TODO: fix case that job lever goes straight to app page like https://jobs.lever.co/amobee/d049864f-6949-4162-80fa-64ab217bd96b/apply?lever-source=Glassdoor
    # TODO: add jobs.jobvite? ProbablyMonsters is one ex that uses, also https://jobs.jobvite.com/the-climate-corporation/job/ojwP9fwx?__jvst=Job+Board&__jvsd=Indeed
    # TODO: https://chj.tbe.taleo.net/? zonar uses, also https://dtt.taleo.net/careersection/10260/jobdetail.ftl?lang=en&job=E20NATCSRCVS022-SA&src=JB-16801
    # TODO: add a check to see if greenhouse or lever pages are embedded into company website, like https://www.docusign.com/company/careers/open?gh_jid=2179621&gh_src=678d46ab1us
    # TODO: and same with https://enview.com/about/careers/jobs?gh_jid=4692323002&gh_src=cba71b432us
    # TODO: add hire.withgoogle.com like https://hire.withgoogle.com/public/jobs/scottyai/view/P_AAAAAADAAADGmyZNJ2hxhI
    # TODO: and https://hire.withgoogle.com/public/jobs/pricecom/view/P_AAAAAADAAADJaeoXf7VANS
    # TODO: add case where there's a visible jobs.lever.io link on the company site page https://scale.com/careers/ac8fc951-e58c-440c-96b3-402d43eab6df, https://jobs.lever.co/ancestry/f59c4078-fdca-4099-92b1-62919728619e/apply or the ACLU
    # TODO: add aperio? https://aperiogroup.bamboohr.com/jobs/view.php?id=110&source=indeed&src=indeed&postedDate=2020-05-04, bamboohr seems popular in finance
    # TODO: add https://jobs.smartrecruiters.com/oneclick-ui/company/103157783/job/1609939482/publication/743999711924474
    else:
        print("Can't process this app :/")
        return "testtesttest"


def html_to_stats(html_text, verbose=False):
    # Get BS from page source, convert to lowercase text blob
    stats_dict = {}
    app_soup = BeautifulSoup(html_text, "html.parser")
    app_text = app_soup.get_text("\n", strip=True).lower()
    stats_dict['app_text'] = [app_text]

    # print text and stats
    # TODO: add app text as verbose or log option?
    # print("APP TEXT: \n", app_text)
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
        word_count = app_text.count(key_word)
        if verbose:
            print(
                "The word {} appears in the application {} times".format(key_word, word_count))
        stats_dict[key_word] = [word_count]
    return stats_dict


def get_all_job_links(soup):
    # Collect all job page links from search results
    job_links = []
    for link in soup.findAll('a', class_="jobtitle turnstileLink"):
        job_links.append(link)

    return job_links


def process_job_url(chrome_driver, job_page_url):
    chrome_driver.get(job_page_url)
    # Check if this is an apply-now job
    is_apply_now = len(chrome_driver.find_elements_by_id('indeedApplyButtonContainer')) == 1

    if is_apply_now:
        print("This is an apply now job!")
        app_text = get_apply_now_text(chrome_driver)


    else:
        print("This is an external application!")
        app_text = get_company_site_text(chrome_driver)

    stats_dict = html_to_stats(app_text)
    stats_dict['is_apply_now'] = [is_apply_now]
    return stats_dict


def next_page_exists(chrome_driver):
    pagination = chrome_driver.find_elements_by_class_name('np')
    if len(pagination) == 1:
        if "Next" in pagination[0].text:
            return True
        else:
            return False
    if len(pagination) == 0:
        return False
    if len(pagination) > 1:
        assert ValueError("Only expect one pagination (np) item per chrome page.")


def get_next_page(chrome_driver):
    try:
        next_page_button = chrome_driver.find_element_by_class_name('np')
    except:
        print("Expected exactly one Next>> elem. Did you validate that next page exists?")
    next_page_button.click()


def run(search_url, chrome_driver):
    # Connect to the search result URL
    # response = requests.get(search_url)
    # cdriver = webdriver.Chrome()
    chrome_driver.get(search_url)

    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(chrome_driver.page_source, "html.parser")

    # Grabbing first job link as an example
    job_links = get_all_job_links(soup)

    # driver = webdriver.Chrome()

    # Get and connect to the first job page URL for df col format
    job_url = 'http://indeed.com/' + job_links[0]['href']
    print("job page url: ", job_url)
    # Scrape the application
    stats_dict = process_job_url(chrome_driver, job_url)
    stats_dict['job_url'] = [job_url]
    df = pd.DataFrame(data=stats_dict)
    chrome_driver.implicitly_wait(5)

    for job in job_links[1:]:
        # Get and connect to the job page URL
        job_url = 'http://indeed.com/' + job['href']
        print("job page url: ", job_url)
        # Scrape the application
        stats_dict = process_job_url(chrome_driver, job_url)
        stats_dict['job_url'] = [job_url]
        df = df.append(pd.DataFrame(data=stats_dict))
        chrome_driver.implicitly_wait(5)

    df.to_csv('job_data.csv')
    print("Done!! :D")


if __name__ == "__main__":
    search_url = APPLY_ON_COMPANY_SITE_CONVOY_URL
    driver = webdriver.Chrome()

    # Test that main data creation for one page works
    run(search_url, driver)

    # Test that pagination works
    driver.get(search_url)
    print("Is there a next page? ", next_page_exists(driver))
    if next_page_exists(driver):
        get_next_page(driver)

    driver.close()
