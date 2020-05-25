from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
from typing import List
from job_structs import IndeedJobInfo, CompanySiteInfo
from constants import WAIT_SHORT, WAIT_LONG, ALL_MLE_SEA_URL, APPLY_ON_COMPANY_SITE_CONVOY_URL
from company_site_helpers import CompanySiteParser

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time


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

    def get_company_site_info(self, indeed_url) -> CompanySiteInfo:
        """
        Gets information from a company site application.
        Assumes driver is already at the indeed job posting url.
        Returns: app type, url, text via CompanySiteInfo object
        """
        # Make sure you're on the indeed link page
        self.driver.get(indeed_url)
        self.driver.implicitly_wait(WAIT_SHORT)

        # Check if this is an apply-now job
        is_apply_now = len(self.driver.find_elements_by_id('indeedApplyButtonContainer')) == 1

        if is_apply_now:
            return CompanySiteInfo.from_dict({'app_type': 'apply now',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_apply_now_text(self.driver)})

        # Click on apply button for on company site
        try:
            link_to_site = self.driver.find_element_by_xpath('//a[text()="Apply On Company Site"]')
        except NoSuchElementException:
            # If we can't find the apply button, don't stop running the program. Allow failure and continue.
            return CompanySiteInfo.from_dict({'app_type': 'error',
                                              'app_url': indeed_url,
                                              'app_text': 'Could not find apply on company site button'})

        self.driver.get(link_to_site.get_attribute('href'))
        self.driver.implicitly_wait(WAIT_SHORT)

        # Process all lever jobs
        if self.driver.current_url.startswith("https://jobs.lever.co"):
            return CompanySiteInfo.from_dict({'app_type': 'lever',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_lever_job_text(self.driver)})

        # Process all greenhouse jobs
        if self.driver.current_url.startswith("https://boards.greenhouse.io/"):
            return CompanySiteInfo.from_dict({'app_type': 'greenhouse',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_greenhouse_job_text(self.driver)})

        # Process greenhouse embedded jobs
        # Ex https://www.docusign.com/company/careers/open?gh_jid=2179621&gh_src=678d46ab1us
        # Ex https://enview.com/about/careers/jobs?gh_jid=4692323002&gh_src=cba71b432us
        # TODO: this doesn't take into account link possibility
        # TODO: this should be a try catch not an if, the if should be the last one to flag that I'm missing a link somehow
        if 'boards.greenhouse.io' in self.driver.page_source:
            return CompanySiteInfo.from_dict({'app_type': 'embedded greenhouse',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_embedded_greenhouse_job_text(
                                                  self.driver)})

        # Process lever jobs that are links on the company apply now page
        # TODO: This doesn't take into account embedding possibility
        # examples are https://scale.com/careers/ac8fc951-e58c-440c-96b3-402d43eab6df
        # https://jobs.lever.co/ancestry/f59c4078-fdca-4099-92b1-62919728619e/apply or the ACLU
        if 'jobs.lever.co' in self.driver.page_source:
            return CompanySiteInfo.from_dict({'app_type': 'lever',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_embedded_lever_job_text(self.driver)})

        # Process if it's a hire with google link
        # Ex https://hire.withgoogle.com/public/jobs/scottyai/view/P_AAAAAADAAADGmyZNJ2hxhI
        # Ex https://hire.withgoogle.com/public/jobs/pricecom/view/P_AAAAAADAAADJaeoXf7VANS
        if self.driver.current_url.startswith("https://hire.withgoogle.com/"):
            return CompanySiteInfo.from_dict({'app_type': 'withgoogle',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_withgoogle_job_text(self.driver)})

        # Process Bamboo HR forms (seems like a finance thing?)
        # https://aperiogroup.bamboohr.com/jobs/view.php?id=110&source=indeed&src=indeed&postedDate=2020-05-04
        if self.driver.current_url.startswith("https://aperiogroup.bamboohr.com"):
            return CompanySiteInfo.from_dict({'app_type': 'bamboohr',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_bamboohr_job_text(self.driver)})

        # Process SmartRecruiters jobs
        # TODO oh gosh this is a tricky one... you can see all the text but only in the script that sets window.__OC_CONTEXT__ =
        # Ex https://www.smartrecruiters.com/Daxko1/743999712591770-software-engineer?trid=998bc6c9-cfbe-4db9-af4b-d7bb8407f264
        # Ex https://jobs.smartrecruiters.com/oneclick-ui/company/103157783/job/1609939482/publication/743999711924474
        if self.driver.current_url.startswith("https://www.smartrecruiters.com"):
            return CompanySiteInfo.from_dict({'app_type': 'smartrecruiters',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_smartrecruiters_job_text(self.driver)})

        # TODO: add jobs.jobvite? ProbablyMonsters is one ex that uses, also https://jobs.jobvite.com/the-climate-corporation/job/ojwP9fwx?__jvst=Job+Board&__jvsd=Indeed
        # TODO: https://chj.tbe.taleo.net/? zonar uses, also https://dtt.taleo.net/careersection/10260/jobdetail.ftl?lang=en&job=E20NATCSRCVS022-SA&src=JB-16801
        else:
            return CompanySiteInfo.from_dict({'app_type': 'unknown',
                                              'app_url': self.driver.current_url,
                                              'app_text': 'unknown - could not parse this app type'})

    def get_job_info(self, soup: BeautifulSoup, page_number: int) -> List[IndeedJobInfo]:
        # Collect all job page links from search results
        jobs = []
        rank = 1

        print("grabbing all jobs in page!")
        for job in soup.findAll('div', class_="jobsearch-SerpJobCard unifiedRow row result clickcard"):
            location = job.find('div', class_="recJobLoc")['data-rc-loc']
            company = job.find('span', class_="company").text.strip()
            print("processing job info for company ", company)
            title = job.find('a', class_="jobtitle turnstileLink")['title']
            indeed_url = 'http://indeed.com/' + job.find('a', class_="jobtitle turnstileLink")['href']
            company_site_info = self.get_company_site_info(indeed_url)
            stats = CompanySiteParser.html_to_stats(company_site_info.app_text)

            job_info = IndeedJobInfo.from_dict({'title': title,
                                                'location': location,
                                                'company': company,
                                                'indeed_url': indeed_url,
                                                'page_number': page_number,
                                                'rank_on_page': rank,
                                                'app_type': company_site_info.app_type,
                                                'company_url': company_site_info.app_url,
                                                'app_text': company_site_info.app_text,
                                                'stats': stats})
            jobs += [job_info]
            rank += 1

        return jobs

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

    @staticmethod
    def get_column_names(job_info) -> List:
        normalized_json = pd.json_normalize([job_info.to_dict()])
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
        self.driver.get(url)
        self.current_search_page = url

        # Parse HTML, grab all job info on page
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        jobs_on_page = self.get_job_info(soup, page_number)

        # Initialize df where we'll store the data
        columns = self.get_column_names(jobs_on_page[0])
        df = pd.DataFrame(columns=columns)
        self.driver.implicitly_wait(WAIT_LONG)

        while True:
            # TODO: seems like this manages to think page 1 is empty when it's not, check?
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            jobs_on_page = self.get_job_info(soup, page_number)

            for job in jobs_on_page:
                # Turn job info struct into a json
                normalized_json = pd.json_normalize([job.to_dict()])
                # Note: passing index 0 okay because we're creating a one row df
                df = df.append(pd.DataFrame(data=normalized_json, index=[0]))
                time.sleep(WAIT_LONG)
                print("Processed job {} on page {}!".format(job.rank_on_page, page_number))

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
    search_url = APPLY_ON_COMPANY_SITE_CONVOY_URL
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
