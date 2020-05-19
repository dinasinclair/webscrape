from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from typing import List, Dict
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime

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


@dataclass_json
@dataclass
class JobInfo:
    app_type: str
    app_text: str
    indeed_url: str
    company_url: str = None
    page_number: int = None
    rank: int = None
    description: str = None  # TODO: make not none, collect during get()
    title: str = None  # TODO: make not none, collect during get()
    stats: Dict = None


@dataclass_json
@dataclass
class QueryInfo:
    query: str
    location: str
    time: datetime
    result: List[JobInfo]


class SearchScraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.pagination_limit = 2

    def print_all_iframes(self) -> None:
        """Prints all iframes in a current driver page source.
        Should not be in a class, should be a general tool"""
        print("all iframes: ")
        iframes = self.driver.find_elements_by_xpath("//iframe")
        print("found {} frames".format(len(iframes)))
        for frame in iframes:
            print(frame)
            print(frame.get_attribute('id'))
            print(frame.get_attribute('title'))

    def print_all_ids_avail(self) -> None:
        """
        Prints all named ids of elements in the self.driver page source.
        Should not be in a class, is a general tool (or at least, static)

        Returns:

        """
        print("all ids:")
        ids = self.driver.find_elements_by_xpath('//*[@id]')
        for ii in ids:
            # if 'apply' in ii.get_attribute('id'):
            print(ii.get_attribute('id'))

    def get_apply_now_text(self) -> JobInfo:
        """
        Gets information from an apply now job.
        Assumes driver is already at an apply now job url.
        Returns: JobInfo object with job details.
        """
        # Find apply button for apply-now scenario
        indeed_url = self.driver.current_url
        apply_button = self.driver.find_element_by_id('indeedApplyButtonContainer')

        # Click on apply button for apply-now
        apply_button.click()
        self.driver.implicitly_wait(1)
        iframe = self.driver.find_element_by_xpath("//iframe[@title='No content']")
        self.driver.switch_to.frame(iframe)
        self.driver.implicitly_wait(1)
        iframe_apply = self.driver.find_element_by_xpath("//iframe[@title='Apply Now']")
        self.driver.switch_to.frame(iframe_apply)
        self.driver.implicitly_wait(1)

        # Create and return JobInfo
        return JobInfo.from_dict({'app_text': self.strip_html(self.driver.page_source),
                                  'app_type': 'apply_now',
                                  'indeed_url': indeed_url})

    def get_company_site_text(self) -> JobInfo:
        """
        Gets information from a company site application.
        Assumes driver is already at the indeed job posting url.
        Returns: JobInfo object with job details.
        """
        # Click on apply button for on company site
        indeed_url = self.driver.current_url
        link_to_site = self.driver.find_element_by_xpath('//a[text()="Apply On Company Site"]')
        self.driver.get(link_to_site.get_attribute('href'))
        self.driver.implicitly_wait(5)
        print("company site url: ", self.driver.current_url)

        # Process all lever jobs
        if self.driver.current_url.startswith("https://jobs.lever.co"):
            print("This is a jobs.lever application")
            # First page is description for lever forms, second page is app questions
            link_to_app = self.driver.find_element_by_xpath('//a[text()="Apply for this job"]')
            self.driver.get(link_to_app.get_attribute('href'))
            return JobInfo.from_dict({'app_text': self.strip_html(self.driver.page_source),
                                      'app_type': 'jobs.lever',
                                      'indeed_url': indeed_url,
                                      'company_url': self.driver.current_url})
        # Process all greenhouse jobs
        if self.driver.current_url.startswith("https://boards.greenhouse.io/"):
            print("This is a boards.greenhouse application")
            # greenhouse jobs put their info on the initial page, no click through needed!
            return JobInfo.from_dict({'app_text': self.strip_html(self.driver.page_source),
                                      'app_type': 'boards.greenhouse',
                                      'indeed_url': indeed_url,
                                      'company_url': self.driver.current_url})
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
            return JobInfo.from_dict({'app_text': "Can't Process",
                                      'app_type': 'unknown',
                                      'indeed_url': indeed_url,
                                      'company_url': self.driver.current_url})

    @staticmethod
    def strip_html(source_page: str) -> str:
        # Get BS from page source, convert to lowercase text blob
        page_soup = BeautifulSoup(source_page, "html.parser")
        return page_soup.get_text("\t", strip=True).lower()

    @staticmethod
    def html_to_stats(html_text: str, verbose: bool = False) -> Dict:
        stats_dict = {}
        app_text = SearchScraper.strip_html(html_text)

        if verbose:
            print("APP TEXT: \n", app_text)

        # store word count in app text for all key words
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
            stats_dict[key_word] = word_count
        return stats_dict

    @staticmethod
    def get_all_job_links(soup: BeautifulSoup) -> List:
        # Collect all job page links from search results
        job_links = []
        for link in soup.findAll('a', class_="jobtitle turnstileLink"):
            job_links.append(link)

        return job_links

    def process_job_url(self, job_url: str) -> JobInfo:
        self.driver.get(job_url)
        # Check if this is an apply-now job
        is_apply_now = len(self.driver.find_elements_by_id('indeedApplyButtonContainer')) == 1

        if is_apply_now:
            print("This is an apply now job!")
            job_info = self.get_apply_now_text()

        else:
            print("This is an external application!")
            job_info = self.get_company_site_text()

        job_info.stats = self.html_to_stats(job_info.app_text)
        print("STATS: ", job_info.stats)
        return job_info

    # TODO make this next page work!!
    def next_page_exists(self) -> bool:
        """
        Returns: bool, true if there is a next page button.
        """
        # pagination = self.driver.find_elements_by_class_name('pagination-list')
        # pagination = self.driver.find_elements_by_xpath("//aria-label")
        # pagination = self.driver.find_element_by_xpath("//div*[@aria-label='Next']")

        pagination = self.driver.find_elements_by_xpath('//*[@aria-label]')

        print (pagination)
        print(len(pagination))
        if len(pagination) == 0:
            return False
        else:
            for elem in pagination:
                aria_label = elem.get_attribute("aria-label")
                print("aria: ", aria_label)
                if aria_label is not None and "Next" in aria_label:
                    return True
        return False

        # if len(pagination) < 2:
        #     aria_label = pagination[-1].find_element_by_css_selector('a').get_attribute("aria-label")
        #     print ("aria: ", aria_label)
        #     if aria_label is not None and "Next" in aria_label:
        #         return True
        #     else:
        #         return False
        # if len(pagination) > 1:
        #     assert ValueError("Only expect one pagination (np) item per chrome page.")

    def get_next_page(self) -> None:
        """
        Navigates to next page of indeed job postings.
        Returns: None
        """
        try:
            next_page_button = self.driver.find_element_by_class_name('np')
        except:
            print("Expected exactly one Next>> elem. Did you validate that next page exists?")
        else:
            next_page_button.click()

    def get_job_normalized_json(self, job_link: str, page_number: int, rank: int):
        job_url = 'http://indeed.com/' + job_link['href']
        print("job page url: ", job_url)
        job_info = self.process_job_url(job_url)
        job_info.page_number = page_number
        job_info.rank = rank
        normalized_json = pd.json_normalize([job_info.to_dict()])
        return normalized_json

    def run(self, search_url):
        """
        Given a specific search URL
        Args:
            search_url:

        Returns:

        """
        # Connect to the search result URL, init page number
        self.driver.get(search_url)
        print("Next page exists? ", self.next_page_exists())
        page_number = 1
        rank = 1

        # Parse HTML and save to BeautifulSoup object
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # Grabbing all job links
        job_links = self.get_all_job_links(soup)

        # Get and connect to the first job page URL for df col format
        normalized_json = self.get_job_normalized_json(job_links[0], page_number, rank)
        df = pd.DataFrame(data=normalized_json, index=[0])
        self.driver.implicitly_wait(5)
        print("Processed job {}!".format(rank))
        rank += 1


        for job in job_links[1:]:
            # Get and connect to the job page URL
            normalized_json = self.get_job_normalized_json(job, page_number, rank)
            # Note: passing index 0 okay because we're creating a one row df
            df = df.append(pd.DataFrame(data=normalized_json, index=[0]))
            self.driver.implicitly_wait(5)
            print("Processed job {}!".format(rank))
            rank += 1
        page_number += 1

        print("about to paginate!")
        print("Next page exists? ", self.next_page_exists())
        print

        # Repeat as long as there's another page to grab
        while self.next_page_exists() and page_number <= self.pagination_limit:
            print("On page {}!".format(page_number))
            self.get_next_page()
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            job_links = self.get_all_job_links(soup)
            for job in job_links:
                # Get and connect to the job page URL
                normalized_json = self.get_job_normalized_json(job, page_number, rank)
                # Note: passing index 0 okay because we're creating a one row df
                df = df.append(pd.DataFrame(data=normalized_json, index=[0]))
                self.driver.implicitly_wait(5)
                print("Processed job {}!".format(rank))
                rank += 1
            page_number += 1

        df.to_csv('job_data.csv')
        print("Done!! :D")


if __name__ == "__main__":
    search_url = ALL_MLE_SEA_URL
    search_scraper = SearchScraper()

    # Test that main data creation for one page works
    search_scraper.run(search_url)

    # Test that pagination works
    search_scraper.driver.get(search_url)
    print("Is there a next page? ", search_scraper.next_page_exists())
    if search_scraper.next_page_exists():
        search_scraper.get_next_page()

    search_scraper.driver.close()
