from bs4 import BeautifulSoup
from selenium import webdriver
from typing import List
from job_structs import IndeedJobInfo, CompanySiteInfo
from constants import WAIT_SHORT, WAIT_LONG, ALL_MLE_SEA_URL
from company_site_helpers import CompanySiteParser
from sql_queries import insert_into_jobs_table
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import popup_helpers
import debugging_tools
import logging


class JobRecorder:

    def __init__(self, current_search_page: str = None):
        self.driver = webdriver.Chrome()
        self.pagination_limit = 10
        self.current_search_page = current_search_page
        if self.current_search_page is not None:
            self.driver.get(current_search_page)

    def get_description(self, indeed_url: str) -> str:
        """
        Given a url to an indeed job posting, returns the string description of that posting.
        Args:
            indeed_url: string url to single job link.

        Returns:
            cleaned string (not html) of job description.
        """
        # Make sure you're on the indeed link page
        if self.driver.current_url != indeed_url:
            self.driver.get(indeed_url)
            self.driver.implicitly_wait(WAIT_SHORT)

        # Grab job description
        try:
            description = self.driver.find_element_by_id('jobDescriptionText')
        except NoSuchElementException:
            logging.warning(f"NoSuchElementException while finding job description at url {indeed_url}")
            return "Error finding description"
        return CompanySiteParser.strip_html(description.get_attribute('innerHTML'))

    def get_company_site_info(self, indeed_url) -> CompanySiteInfo:
        """
        Gets information from a company site application.
        Assumes driver is already at the indeed job posting url.
        Returns: app type, url, text via CompanySiteInfo object
        """
        # Make sure you're on the indeed link page
        if self.driver.current_url != indeed_url:
            self.driver.get(indeed_url)
            self.driver.implicitly_wait(WAIT_LONG)

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

        # TODO: https://chj.tbe.taleo.net/? zonar uses, also https://dtt.taleo.net/careersection/10260/jobdetail.ftl?lang=en&job=E20NATCSRCVS022-SA&src=JB-16801
        # TODO: add apply with indeed embedded in company site https://www.kforce.com/Jobs/job.aspx?job=1696~TVT~1896026T1~99&id=2128&utm_source=Indeed&utm_medium=PPC&utm_campaign=Indeed-PPC#/?_k=gqcchp

        if self.driver.current_url.startswith("https://careers.twitter.com"):
            return CompanySiteInfo.from_dict({'app_type': 'twitter',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_twitter_job_text(self.driver)})

        if self.driver.current_url.startswith("https://www.facebook.com/careers/"):
            return CompanySiteInfo.from_dict({'app_type': 'facebook',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_facebook_job_text(self.driver)})

        if self.driver.current_url.startswith("http://jobs.jobvite.com/"):
            return CompanySiteInfo.from_dict({'app_type': 'jobvite',
                                              'app_url': self.driver.current_url,
                                              'app_text': CompanySiteParser.get_jobvite_job_text(self.driver)})

        if 'workday' in self.driver.page_source:
            return CompanySiteInfo.from_dict({'app_type': 'workday',
                                              'app_url': self.driver.current_url,
                                              'app_text': 'cannot parse'})

        if len(self.driver.find_elements_by_xpath('//a[contains(@href, "mailto")]')) > 0:
            # TODO: this gets false positives like https://www.governmentjobs.com/careers/tacoma/jobs/2735787/machine-learning-engineer and amazon
            # Ex https://lexion.ai/senior-machine-learning-engineer
            return CompanySiteInfo.from_dict({'app_type': 'mailto',
                                              'app_url': self.driver.current_url,
                                              'app_text': 'no form to parse'})

        else:
            return CompanySiteInfo.from_dict({'app_type': 'unknown',
                                              'app_url': self.driver.current_url,
                                              'app_text': 'cannot parse'})

    def write_jobs_in_page_to_db(self,
                                 conn,
                                 soup: BeautifulSoup,
                                 page_number: int,
                                 query_id: int) -> List[IndeedJobInfo]:
        """
        Collect all job page links from search results
        Args:
            query_id:
            conn:
            soup:
            page_number:

        Returns:

        """
        # Initialize arrays and page rank as needed
        jobs = []
        rank = 1

        logging.info(f"Grabbing all jobs in page for page {page_number}!")
        for job in soup.findAll('div', class_="jobsearch-SerpJobCard unifiedRow row result clickcard"):
            # Find relevant job details within the indeed job posting page
            location = job.find('div', class_="recJobLoc")['data-rc-loc']
            company = job.find('span', class_="company").text.strip()
            title = job.find('a', class_="jobtitle turnstileLink")['title']
            indeed_url = 'http://indeed.com' + job.find('a', class_="jobtitle turnstileLink")['href']
            description = self.get_description(indeed_url)

            # Find additional information as needed from the company site
            company_site_info = self.get_company_site_info(indeed_url)
            stats = CompanySiteParser.html_to_stats(company_site_info.app_text)

            # Quick log of job info
            logging.info(f"processing job info for company {company}")
            logging.info(f"This is a {company_site_info.app_type} job")
            logging.debug(f"indeed url: {indeed_url}")
            logging.debug(f"description: {description}")

            # Save job in IndeedJobInfo format
            job_info = IndeedJobInfo.from_dict({'title': title,
                                                'location': location,
                                                'company': company,
                                                'indeed_url': indeed_url,
                                                'page_number': page_number,
                                                'rank_on_page': rank,
                                                'app_type': company_site_info.app_type,
                                                'company_url': company_site_info.app_url,
                                                'app_text': company_site_info.app_text,
                                                'stats': stats,
                                                'description': description})

            self.write_job_to_db(conn, job_info, query_id)
            logging.info(f"Processed job {job_info.rank_on_page} on page {page_number}!")

            # Update jobs array and page ranking, making sure to wait after each job to be a friendly scraper!
            jobs += [job_info]
            rank += 1
            time.sleep(WAIT_SHORT)

        return jobs

    def next_page_exists(self) -> bool:
        """
        Returns: bool, true if there is a next page button.
        """
        # Re-centers to search screen (rather than individual job pages)
        self.driver.implicitly_wait(WAIT_LONG)
        self.driver.get(self.current_search_page)
        self.driver.implicitly_wait(WAIT_LONG)

        # Looks through all aria labels (there's a "next" and "previous" if either exists)
        pagination = self.driver.find_elements_by_xpath("//*[@aria-label='Next']")

        # TODO: use find element rather than find elements, or somehow call out if there's more than one next button?
        logging.info(f"next page exists called on {self.driver.current_url}")
        logging.info(f"found {len(pagination)} elements with Next label")
        if len(pagination) == 0:
            return False
        else:
            return True

    def get_next_page(self) -> None:
        """
        Navigates to next page of indeed job postings.
        Returns: None
        """
        # self.driver.implicitly_wait(WAIT_LONG)

        try:
            next_page_button = self.driver.find_element_by_xpath("//*[@aria-label='Next']")
            logging.debug(f"Next page button element: {next_page_button}")
            time.sleep(1)
            next_page_button.click()
        except ElementClickInterceptedException as e:
            logging.warning("oh no, popup during next page click!")
            self.driver.implicitly_wait(WAIT_SHORT)
            popup_helpers.remove_legal_popup(self.driver)
            self.driver.implicitly_wait(WAIT_SHORT)
            popup_helpers.remove_popover_popup(self.driver)
            self.driver.implicitly_wait(WAIT_SHORT)

            # TODO(dsinc) make this cleaner, for now we're just trying the above code 2x to try to stop fails?
            time.sleep(1)
            logging.warning("Trying to close legal popups a second time, just in case!")
            popup_helpers.remove_legal_popup(self.driver)
            self.driver.implicitly_wait(WAIT_SHORT)
            time.sleep(1)

            # Click the next page button after removing popups! Hope there's no error now...
            self.driver.implicitly_wait(WAIT_SHORT)
            next_page_button = self.driver.find_element_by_xpath("//*[@aria-label='Next']")
            next_page_button.click()

        self.driver.implicitly_wait(WAIT_SHORT)
        self.current_search_page = self.driver.current_url

    def write_all_jobs_to_db(self, query_url: str, conn, query_id: int) -> None:
        """
        Writes all jobs to DB for a given query url.
        Args:
            query_url: url of initial query page with jobs returned
            conn: connection to the job DB
            query_id: int ID identifying the query instance

        Returns:
            None, just writes to DB
        """
        # Initialize counts and url position
        page_number = 1
        self.driver.get(query_url)
        self.current_search_page = query_url

        while page_number <= self.pagination_limit:
            # Get all jobs on current page
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            self.write_jobs_in_page_to_db(conn, soup, page_number, query_id)

            # Get next page of jobs, if it exists! Otherwise you're done with this query
            # The next_page_exists call fails when it shouldn't sometimes, so we'll try it 2x here and see if that
            # helps?
            if self.next_page_exists():
                self.get_next_page()
                page_number += 1
            # TODO(dsinc): this is how I'm trying next_page_exists 2x... clean this up?
            elif self.next_page_exists():
                logging.warning("Found no next page, trying a second time.")
                self.get_next_page()
                page_number += 1
            else:
                break
        logging.info("Done writing all jobs to DB!! :D")

    @staticmethod
    def write_job_to_db(conn, job_info: IndeedJobInfo, query_id: int):
        """

        Args:
            conn:
            job_info:
            query_id:

        Returns:

        """
        cur = conn.cursor()
        cur.execute(insert_into_jobs_table, (
            query_id,
            job_info.app_type,
            job_info.app_text,
            job_info.company,
            job_info.title,
            job_info.description,
            job_info.company_url,
            job_info.indeed_url,
            job_info.page_number,
            job_info.rank_on_page
        ))
        conn.commit()
        logging.info(f"lastrow of jobs: {cur.lastrowid}")
        return cur.lastrowid


if __name__ == "__main__":
    job_recorder = JobRecorder()

    # Test that main data creation for one page works
    job_recorder.run(ALL_MLE_SEA_URL, 'output_files/job_data_mle_sea.csv')

    # Test that pagination works
    # job_recorder.driver.get(search_url)
    # print("Is there a next page? ", job_recorder.next_page_exists())
    # job_recorder.driver.implicitly_wait(WAIT_SHORT)
    # if job_recorder.next_page_exists():
    #     job_recorder.driver.implicitly_wait(WAIT_SHORT)
    #     job_recorder.get_next_page()
    #     job_recorder.driver.implicitly_wait(WAIT_SHORT)
    #     print("driver url: ", job_recorder.driver.current_url)
    #     job_recorder.driver.implicitly_wait(WAIT_SHORT)
    #     print("current_page: ", job_recorder.current_search_page)

    job_recorder.driver.close()
