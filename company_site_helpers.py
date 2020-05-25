from constants import WAIT_SHORT
from bs4 import BeautifulSoup
from typing import Dict


class CompanySiteParser:

    @staticmethod
    def strip_html(source_page: str) -> str:
        # Get BS from page source, convert to lowercase text blob
        page_soup = BeautifulSoup(source_page, "html.parser")
        return page_soup.get_text("\t", strip=True).lower()

    @staticmethod
    def html_to_stats(html_text: str, verbose: bool = True) -> Dict[str, int]:
        stats_dict = {}
        app_text = CompanySiteParser.strip_html(html_text)

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
    def get_apply_now_text(driver) -> str:
        """
        Gets information from an apply now job.
        Assumes driver is already at an apply now job url.
        Returns: IndeedJobInfo object with job details.
        """
        print("This is an apply now application")
        # Find apply button for apply-now scenario
        apply_button = driver.find_element_by_id('indeedApplyButtonContainer')

        # Click on apply button for apply-now
        apply_button.click()
        driver.implicitly_wait(WAIT_SHORT)
        iframe = driver.find_element_by_xpath("//iframe[@title='No content']")
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(WAIT_SHORT)
        iframe_apply = driver.find_element_by_xpath("//iframe[@title='Apply Now']")
        driver.switch_to.frame(iframe_apply)
        driver.implicitly_wait(WAIT_SHORT)

        return CompanySiteParser.strip_html(driver.page_source)

    @staticmethod
    def get_lever_job_text(driver) -> str:
        print("This is a jobs.lever application")
        # There are two structures here: straight to application, or description than application.
        # Case 1: straight to application (ex. https://jobs.lever.co/grabango/7ff6e367-6523-4ca2-b630-57a46881e467/apply?lever-source=Glassdoor)
        try:
            driver.find_element_by_class_name('application page')
        # Case 2: first page is description for lever forms, second page is app questions (like https://jobs.lever.co/blueowl/4a01e48e-8602-4f76-a87c-6ad16b63b2a1?lever-source=IndeedSponsored)
        except:  # TODO add the right exception type here
            driver.find_element_by_class_name(
                'posting-page')  # TODO this could cause an error two, should I bother to catch that?
            link_to_app = driver.find_element_by_xpath('//a[text()="Apply for this job"]')
            driver.get(link_to_app.get_attribute('href'))
            driver.implicitly_wait(WAIT_SHORT)

        return CompanySiteParser.strip_html(driver.page_source)

    @staticmethod
    def get_greenhouse_job_text(driver) -> str:
        print("This is a boards.greenhouse application")
        # greenhouse jobs put their info on the initial page, no click through needed!
        return CompanySiteParser.strip_html(driver.page_source)

    @staticmethod
    def get_embedded_greenhouse_job_text(driver) -> str:
        # Process greenhouse embedded jobs
        # Ex https://www.docusign.com/company/careers/open?gh_jid=2179621&gh_src=678d46ab1us
        # Ex https://enview.com/about/careers/jobs?gh_jid=4692323002&gh_src=cba71b432us
        # TODO: this doesn't take into account link possibility
        # TODO: this should be a try catch not an if, the if should be the last one to flag that I'm missing a link somehow
        print("this is an embedded greenhouse application")
        embedded_app = driver.find_element_by_xpath('//form[contains(@action, "greenhouse.io"]')
        return CompanySiteParser.strip_html(embedded_app.text)

    @staticmethod
    def get_embedded_lever_job_text(driver) -> str:
        # Process lever jobs that are links on the company apply now page
        # TODO: This doesn't take into account embedding possibility
        # examples are https://scale.com/careers/ac8fc951-e58c-440c-96b3-402d43eab6df
        # https://jobs.lever.co/ancestry/f59c4078-fdca-4099-92b1-62919728619e/apply or the ACLU

        print("this is a link lever.co application")
        app_link = driver.find_element_by_xpath('//a[contains(@href, "lever.co"]')
        app_link.click()
        driver.implicitly_wait(WAIT_SHORT)

        # TODO: this will check that we're on the app page but then just fail if you're not...
        driver.find_element_by_class_name('application page')
        return CompanySiteParser.strip_html(driver.page_source)

    @staticmethod
    def get_withgoogle_job_text(driver) -> str:
        # Process if it's a hire with google link
        # Ex https://hire.withgoogle.com/public/jobs/scottyai/view/P_AAAAAADAAADGmyZNJ2hxhI
        # Ex https://hire.withgoogle.com/public/jobs/pricecom/view/P_AAAAAADAAADJaeoXf7VANS
        # TODO: this currently fails if it can't find this class name, correct call?
        print("this is a hire.withgoogle application")
        app_form = driver.find_element_by_class_name('bb-jobs-application__container')
        return CompanySiteParser.strip_html(app_form.text())

    @staticmethod
    def get_bamboohr_job_text(driver) -> str:
        # Process Bamboo HR forms (seems like a finance thing?)
        # https://aperiogroup.bamboohr.com/jobs/view.php?id=110&source=indeed&src=indeed&postedDate=2020-05-04
        print("this is a aperiogroup.bamboohr application")
        app_form = driver.find_element_by_id('applicationForm')
        return CompanySiteParser.strip_html(app_form.text())

    @staticmethod
    def get_smartrecruiters_job_text(driver) -> str:
        # Process SmartRecruiters jobs
        # TODO oh gosh this is a tricky one... you can see all the text but only in the script that sets window.__OC_CONTEXT__ =
        # Ex https://www.smartrecruiters.com/Daxko1/743999712591770-software-engineer?trid=998bc6c9-cfbe-4db9-af4b-d7bb8407f264
        # Ex https://jobs.smartrecruiters.com/oneclick-ui/company/103157783/job/1609939482/publication/743999711924474
        print("this is a smartrecruiters application")
        try:
            interested_button = driver.find_element_by_xpath('//a[text()="I\'m interested"]')
            interested_button.click()
            driver.implicitly_wait(WAIT_SHORT)
        except:
            pass

        # TODO: have to give raw text which is a mess, unless I can figure out better way to parse the script labels?
        return driver.page_source
