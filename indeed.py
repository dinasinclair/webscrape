from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from typing import List, Dict
from job_structs import JobInfo

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time

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
# Square is an example of a smartrecruiters job with pronoun questions!

WAIT_LONG = 10
WAIT_SHORT = 5


class SearchScraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.pagination_limit = 5
        self.current_search_page = None

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

    def get_apply_now_text(self, job_info: JobInfo) -> JobInfo:
        """
        Gets information from an apply now job.
        Assumes driver is already at an apply now job url.
        Returns: JobInfo object with job details.
        """
        # Find apply button for apply-now scenario
        apply_button = self.driver.find_element_by_id('indeedApplyButtonContainer')

        # Click on apply button for apply-now
        apply_button.click()
        self.driver.implicitly_wait(WAIT_SHORT)
        iframe = self.driver.find_element_by_xpath("//iframe[@title='No content']")
        self.driver.switch_to.frame(iframe)
        self.driver.implicitly_wait(WAIT_SHORT)
        iframe_apply = self.driver.find_element_by_xpath("//iframe[@title='Apply Now']")
        self.driver.switch_to.frame(iframe_apply)
        self.driver.implicitly_wait(WAIT_SHORT)

        job_info.app_text = self.strip_html(self.driver.page_source)
        job_info.app_type = 'apply_now'

        # Return enriched JobInfo
        return job_info

    def get_company_site_text(self, job_info: JobInfo) -> JobInfo:
        """
        Gets information from a company site application.
        Assumes driver is already at the indeed job posting url.
        Returns: JobInfo object with job details.
        """
        # Click on apply button for on company site
        try:
            link_to_site = self.driver.find_element_by_xpath('//a[text()="Apply On Company Site"]')
        except NoSuchElementException:
            # If we can't find the apply button, don't stop running the program. Allow failure and continue.
            job_info.app_text = 'Error. Didn\'t find Apply On Company Site button'
            job_info.app_type = 'Apply On Company Site Error'
            return job_info

        self.driver.get(link_to_site.get_attribute('href'))
        self.driver.implicitly_wait(WAIT_SHORT)

        # Process all lever jobs
        if self.driver.current_url.startswith("https://jobs.lever.co"):
            print("This is a jobs.lever application")
            # There are two structures here: straight to application, or description than application.
            # Case 1: straight to application (ex. https://jobs.lever.co/grabango/7ff6e367-6523-4ca2-b630-57a46881e467/apply?lever-source=Glassdoor)
            try:
                self.driver.find_element_by_class_name('content-wrapper application page')
            # Case 2: first page is description for lever forms, second page is app questions (like https://jobs.lever.co/blueowl/4a01e48e-8602-4f76-a87c-6ad16b63b2a1?lever-source=IndeedSponsored)
            except:  # TODO add the right exception type here
                self.driver.find_element_by_class_name(
                    'content-wrapper posting page')  # TODO this could cause an error two, should I bother to catch that?
                link_to_app = self.driver.find_element_by_xpath('//a[text()="Apply for this job"]')
                self.driver.get(link_to_app.get_attribute('href'))
                self.driver.implicitly_wait(WAIT_SHORT)

            job_info.app_text = self.strip_html(self.driver.page_source)
            job_info.app_type = 'jobs.lever'
            job_info.company_url = self.driver.current_url
            return job_info

        # Process all greenhouse jobs
        if self.driver.current_url.startswith("https://boards.greenhouse.io/"):
            print("This is a boards.greenhouse application")
            # greenhouse jobs put their info on the initial page, no click through needed!
            job_info.app_text = self.strip_html(self.driver.page_source)
            job_info.app_type = 'boards.greenhouse'
            job_info.company_url = self.driver.current_url
            return job_info

        # Process greenhouse embedded jobs
        # Ex https://www.docusign.com/company/careers/open?gh_jid=2179621&gh_src=678d46ab1us
        # Ex https://enview.com/about/careers/jobs?gh_jid=4692323002&gh_src=cba71b432us
        # TODO: this doesn't take into account link possibility
        # TODO: this should be a try catch not an if, the if should be the last one to flag that I'm missing a link somehow
        if 'boards.greenhouse.io' in self.driver.page_source.text():
            print("this is an embedded greenhouse application")
            embedded_app = self.driver.find_element_by_xpath('//form[contains(@action, "greenhouse.io"]')
            job_info.app_text = self.strip_html(embedded_app.text)
            job_info.app_type = 'embedded boards.greenhouse'
            job_info.company_url = self.driver.current_url

        # Process lever jobs that are links on the company apply now page
        # TODO: This doesn't take into account embedding possibility
        # examples are https://scale.com/careers/ac8fc951-e58c-440c-96b3-402d43eab6df
        # https://jobs.lever.co/ancestry/f59c4078-fdca-4099-92b1-62919728619e/apply or the ACLU
        if 'jobs.lever.co' in self.driver.page_source.text():
            print("this is a link lever.co application")
            app_link = self.driver.find_element_by_xpath('//a[contains(@href, "lever.co"]')
            app_link.click()
            self.driver.implicitly_wait(WAIT_SHORT)

            # TODO: this will check that we're on the app page but then just fail if you're not...
            self.driver.find_element_by_class_name('content-wrapper application page')
            job_info.app_text = self.strip_html(self.driver.page_source)
            job_info.app_type = 'jobs.lever'
            job_info.company_url = self.driver.current_url

        # Process if it's a hire with google link
        # Ex https://hire.withgoogle.com/public/jobs/scottyai/view/P_AAAAAADAAADGmyZNJ2hxhI
        # Ex https://hire.withgoogle.com/public/jobs/pricecom/view/P_AAAAAADAAADJaeoXf7VANS
        if self.driver.current_url.startswith("https://hire.withgoogle.com/"):
            # TODO: this currently fails if it can't find this class name, correct call?
            print("this is a hire.withgoogle application")
            app_form = self.driver.find_element_by_class_name('bb-jobs-application__container')
            job_info.app_text = self.strip_html(app_form.text())
            job_info.app_type = 'hire.withgoogle'
            job_info.company_url = self.driver.current_url

        # Process Bamboo HR forms (seems like a finance thing?)
        # https://aperiogroup.bamboohr.com/jobs/view.php?id=110&source=indeed&src=indeed&postedDate=2020-05-04
        if self.driver.current_url.startswith("https://aperiogroup.bamboohr.com"):
            print("this is a aperiogroup.bamboohr application")
            app_form = self.driver.find_element_by_id('applicationForm')
            job_info.app_text = self.strip_html(app_form.text())
            job_info.app_type = 'aperiogroup.bamboohr'
            job_info.company_url = self.driver.current_url

        # Process SmartRecruiters jobs
        # TODO oh gosh this is a tricky one... you can see all the text but only in the script that sets window.__OC_CONTEXT__ =
        # Ex https://www.smartrecruiters.com/Daxko1/743999712591770-software-engineer?trid=998bc6c9-cfbe-4db9-af4b-d7bb8407f264
        # Ex https://jobs.smartrecruiters.com/oneclick-ui/company/103157783/job/1609939482/publication/743999711924474
        if self.driver.current_url.startswith("https://www.smartrecruiters.com"):
            print("this is a smartrecruiters application")
            try:
                interested_button = self.driver.find_element_by_xpath('//a[text()="I\'m interested"]')
                interested_button.click()
                self.driver.implicitly_wait(WAIT_SHORT)
            except:
                pass

            # TODO: have to give raw text which is a mess, unless I can figure out better way to parse the script labels?
            job_info.app_text = self.strip_html(self.driver.page_source)
            job_info.app_type = 'smartrecruiters'
            job_info.company_url = self.driver.current_url

        # TODO: add jobs.jobvite? ProbablyMonsters is one ex that uses, also https://jobs.jobvite.com/the-climate-corporation/job/ojwP9fwx?__jvst=Job+Board&__jvsd=Indeed
        # TODO: https://chj.tbe.taleo.net/? zonar uses, also https://dtt.taleo.net/careersection/10260/jobdetail.ftl?lang=en&job=E20NATCSRCVS022-SA&src=JB-16801
        else:
            print("Can't process this app :/")
            job_info.app_text = "Can't Process"
            job_info.app_type = 'unknown'
            job_info.company_url = self.driver.current_url
            return job_info

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
    def get_basic_job_info_from_cards(soup: BeautifulSoup, page_number: int) -> List[JobInfo]:
        # Collect all job page links from search results
        jobs = []

        print("grabbing all jobs in page!")
        for job in soup.findAll('div', class_="jobsearch-SerpJobCard unifiedRow row result clickcard"):
            location = job.find('div', class_="recJobLoc")['data-rc-loc']
            company = job.find('span', class_="company").text.strip()
            title = job.find('a', class_="jobtitle turnstileLink")['title']
            indeed_url = 'http://indeed.com/' + job.find('a', class_="jobtitle turnstileLink")['href']

            job_info = JobInfo.from_dict({'title': title,
                                          'location': location,
                                          'company': company,
                                          'indeed_url': indeed_url,
                                          'page_number': page_number})
            jobs += [job_info]

        return jobs

    def add_text_to_job_info(self, job_info: JobInfo) -> JobInfo:
        self.driver.get(job_info.indeed_url)
        time.sleep(WAIT_SHORT)
        # Check if this is an apply-now job
        is_apply_now = len(self.driver.find_elements_by_id('indeedApplyButtonContainer')) == 1

        if is_apply_now:
            print("This is an apply now job!")
            job_info = self.get_apply_now_text(job_info)

        else:
            print("This is an external application!")
            job_info = self.get_company_site_text(job_info)

        job_info.stats = self.html_to_stats(job_info.app_text)
        print("STATS: ", job_info.stats)
        return job_info

    def next_page_exists(self) -> bool:
        """
        Returns: bool, true if there is a next page button.
        """
        # Re-centers to search screen (rather than individual job pages)
        self.driver.implicitly_wait(WAIT_SHORT)
        self.driver.get(self.current_search_page)
        self.driver.implicitly_wait(WAIT_SHORT)

        # Looks through all aria labels (there's a "next" and "previous" if either exists)
        pagination = self.driver.find_elements_by_xpath("//*[@aria-label='Next']")

        # TODO: use find element rather than find elements, or somehow call out if there's more than one next button?
        print("next page exists called on ", self.driver.current_url)
        print("found {} elements with Next label".format(len(pagination)))
        if len(pagination) == 0:
            return False
        else:
            return True

    def get_next_page(self) -> None:
        """
        Navigates to next page of indeed job postings.
        Returns: None
        """
        self.driver.implicitly_wait(WAIT_SHORT)
        # TODO: is this the right error handling method? idk if it just prints but continues...
        try:
            next_page_button = self.driver.find_element_by_xpath("//*[@aria-label='Next']")
        except:
            print("Expected exactly one Next elem. Did you validate that next page exists?")
        try:
            next_page_button.click()
        except ElementClickInterceptedException:
            print("oh no, popup!")
            close_window_button = self.driver.find_element_by_id('popover-x')
            close_window_button.click()

        self.driver.implicitly_wait(WAIT_SHORT)
        self.current_search_page = self.driver.current_url

    def get_job_normalized_json(self, job_info: JobInfo, rank: int):
        job_info = self.add_text_to_job_info(job_info)
        job_info.rank = rank
        normalized_json = pd.json_normalize([job_info.to_dict()])
        return normalized_json

    def get_column_names(self, job) -> List:
        normalized_json = self.get_job_normalized_json(job, rank=1)
        df = pd.DataFrame(data=normalized_json, index=[0])
        return df.columns

    def run(self, url: str):
        """
        Given a specific search URL
        Args:
            url:

        Returns:

        """
        # Initialize counts and url position
        page_number = 1
        rank = 1
        self.driver.get(url)
        self.current_search_page = url

        # Parse HTML, grab all job links on page
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        jobs_on_page = self.get_basic_job_info_from_cards(soup, page_number)

        # Initialize df where we'll store the data
        columns = self.get_column_names(jobs_on_page[0])
        df = pd.DataFrame(columns=columns)
        self.driver.implicitly_wait(WAIT_LONG)

        while True:
            # TODO: seems like this manages to think page 1 is empty when it's not, check?
            print("On page {}!".format(page_number))
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            jobs_on_page = self.get_basic_job_info_from_cards(soup, page_number)

            for job in jobs_on_page:
                # Get and connect to the job page URL
                normalized_json = self.get_job_normalized_json(job, rank)
                # Note: passing index 0 okay because we're creating a one row df
                df = df.append(pd.DataFrame(data=normalized_json, index=[0]))
                time.sleep(WAIT_LONG)
                print("Processed job {}!".format(rank))
                rank += 1

            # TODO: write small chunks to csv so that if it pauses midway through you don't lose all data?

            # Repeat as long as there's another page to grab and we're under the limit
            if not self.next_page_exists() or page_number >= self.pagination_limit:
                break
            else:
                self.get_next_page()
                page_number += 1

        df = df.reset_index(drop=True)
        df.to_csv('job_data.csv')
        print("Done!! :D")


if __name__ == "__main__":
    search_url = ALL_MLE_SEA_URL
    search_scraper = SearchScraper()

    # Test that main data creation for one page works
    search_scraper.run(search_url)

    # Test that pagination works
    # search_scraper.driver.get(search_url)
    # print("Is there a next page? ", search_scraper.next_page_exists())
    # search_scraper.driver.implicitly_wait(WAIT_SHORT)
    # if search_scraper.next_page_exists():
    #     search_scraper.driver.implicitly_wait(WAIT_SHORT)
    #     search_scraper.get_next_page()
    #     search_scraper.driver.implicitly_wait(WAIT_SHORT)
    #     print("driver url: ", search_scraper.driver.current_url)
    #     search_scraper.driver.implicitly_wait(WAIT_SHORT)
    #     print("current_page: ", search_scraper.current_search_page)

    search_scraper.driver.close()

# TODO: if fails to find element, fail elegantly rather than throw error
