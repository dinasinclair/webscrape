from constants import WAIT_SHORT, WAIT_LONG, KEY_WORDS
from bs4 import BeautifulSoup
from typing import Dict
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import popup_helpers
import time


class CompanySiteParser:

    @staticmethod
    def strip_html(source_page: str) -> str:
        # Get BS from page source, convert to lowercase text blob
        page_soup = BeautifulSoup(source_page, "html.parser")
        return page_soup.get_text("\t", strip=True).lower()

    @staticmethod
    def html_to_stats(html_text: str, verbose: bool = False) -> Dict[str, int]:
        stats_dict = {}
        app_text = CompanySiteParser.strip_html(html_text)

        if verbose:
            print("APP TEXT: \n", app_text)

        # store word count in app text for all key words
        for key_word in KEY_WORDS:
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

        try:
            # Find apply button for apply-now scenario
            apply_button = driver.find_element_by_id('indeedApplyButtonContainer')
            time.sleep(1)
            apply_button.click()
        except ElementClickInterceptedException as e:
            print("oh no, popup during apply_now click!")
            driver.implicitly_wait(WAIT_SHORT)
            popup_helpers.remove_legal_popup(driver)
            driver.implicitly_wait(WAIT_SHORT)
            popup_helpers.remove_popover_popup(driver)
            driver.implicitly_wait(WAIT_SHORT)

            # Click the next page button after removing popups! Hope there's no error now...
            apply_button = driver.find_element_by_id('indeedApplyButtonContainer')
            time.sleep(1)
            apply_button.click()

        # Find that apply now text in the right iframe!
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
        # There are two structures here: straight to application, or description than application.
        # Case 1: straight to application (ex. https://jobs.lever.co/grabango/7ff6e367-6523-4ca2-b630-57a46881e467/apply?lever-source=Glassdoor)
        try:
            driver.find_element_by_class_name('application-page')
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
        # greenhouse jobs put their info on the initial page, no click through needed!
        return CompanySiteParser.strip_html(driver.page_source)

    @staticmethod
    def get_embedded_greenhouse_job_text(driver) -> str:
        # Process greenhouse embedded jobs
        # Ex https://www.docusign.com/company/careers/open?gh_jid=2179621&gh_src=678d46ab1us
        # Ex https://enview.com/about/careers/jobs?gh_jid=4692323002&gh_src=cba71b432us
        try:
            embedded_iframe = driver.find_element_by_xpath('//iframe[contains(@src, "greenhouse")]')
            driver.switch_to.frame(embedded_iframe)
            driver.implicitly_wait(WAIT_LONG)
            embedded_app = driver.find_element_by_xpath('//form[contains(@action, "greenhouse")]')
            return CompanySiteParser.strip_html(embedded_app.get_attribute('innerHTML'))
        except NoSuchElementException:
            # Second method: look for a greenhouse link and follow it
            try:
                app_link = driver.find_element_by_xpath('//a[contains(@href, "greenhouse")]')
                driver.get(app_link.get_attribute('href'))
                driver.implicitly_wait(WAIT_SHORT)
                return CompanySiteParser.strip_html(driver.page_source)
            except NoSuchElementException:
                return "error getting embedded text"

    @staticmethod
    def get_embedded_lever_job_text(driver) -> str:
        # Process lever jobs that are links on the company apply now page
        # TODO: This doesn't take into account embedding possibility
        # examples are https://scale.com/careers/ac8fc951-e58c-440c-96b3-402d43eab6df
        # https://jobs.lever.co/ancestry/f59c4078-fdca-4099-92b1-62919728619e/apply or the ACLU
        app_link = driver.find_element_by_xpath('//a[contains(@href, "lever.co")]')
        # was having trouble clicking the button since I was sometimes finding a hidden mobile button that couldn't be clicked, so
        driver.get(app_link.get_attribute('href'))
        driver.implicitly_wait(WAIT_SHORT)

        # TODO: this will check that we're on the app page but then just fail if you're not...
        app_form = driver.find_element_by_class_name('application-page')
        return CompanySiteParser.strip_html(app_form.get_attribute('innerHTML'))

    @staticmethod
    def get_withgoogle_job_text(driver) -> str:
        # Process if it's a hire with google link
        # Ex https://hire.withgoogle.com/public/jobs/scottyai/view/P_AAAAAADAAADGmyZNJ2hxhI
        # Ex https://hire.withgoogle.com/public/jobs/pricecom/view/P_AAAAAADAAADJaeoXf7VANS
        # TODO: this currently fails if it can't find this class name, correct call?
        app_form = driver.find_element_by_class_name('bb-jobs-application__container')
        return CompanySiteParser.strip_html(app_form.get_attribute('innerHTML'))

    @staticmethod
    def get_bamboohr_job_text(driver) -> str:
        # Process Bamboo HR forms (seems like a finance thing?)
        # https://aperiogroup.bamboohr.com/jobs/view.php?id=110&source=indeed&src=indeed&postedDate=2020-05-04
        app_form = driver.find_element_by_id('applicationForm')
        return CompanySiteParser.strip_html(app_form.get_attribute('innerHTML'))

    @staticmethod
    def get_twitter_job_text(driver) -> str:
        app_form = driver.find_element_by_class_name('form-inside')
        return CompanySiteParser.strip_html(app_form.get_attribute('innerHTML'))

    @staticmethod
    def get_facebook_job_text(driver) -> str:
        apply_button = driver.find_element_by_xpath('//a[text()="Apply to Job"]')
        link_to_app = apply_button.get_attribute('href')
        driver.get(link_to_app)
        driver.implicitly_wait(WAIT_SHORT)
        app_form = driver.find_element_by_xpath("//form")
        return CompanySiteParser.strip_html(app_form.get_attribute('innerHTML'))

    @staticmethod
    def get_smartrecruiters_job_text(driver) -> str:
        # Process SmartRecruiters jobs
        # TODO oh gosh this is a tricky one... you can see all the text but only in the script that sets window.__OC_CONTEXT__ =
        # Ex https://www.smartrecruiters.com/Daxko1/743999712591770-software-engineer?trid=998bc6c9-cfbe-4db9-af4b-d7bb8407f264
        # Ex https://jobs.smartrecruiters.com/oneclick-ui/company/103157783/job/1609939482/publication/743999711924474
        try:
            interested_button = driver.find_element_by_xpath('//a[text()="I\'m interested"]')
            interested_button.click()
            driver.implicitly_wait(WAIT_SHORT)
        except:
            pass

        # TODO: have to give raw text which is a mess, unless I can figure out better way to parse the script labels?
        return driver.page_source

    @staticmethod
    def get_jobvite_job_text(driver) -> str:
        # Process SmartRecruiters jobs
        # TODO oh gosh this is a tricky one... you can see all the text but only in the script
        # Ex http://jobs.jobvite.com/careers/inrix/job/oezIcfwr?__jvst=Job+Board&__jvsd=Indeed
        # Ex https://jobs.jobvite.com/the-climate-corporation/job/ojwP9fwx?__jvst=Job+Board&__jvsd=Indeed
        try:
            apply_button = driver.find_element_by_xpath('//a[text()="Apply"]')
            apply_button.click()
            driver.implicitly_wait(WAIT_LONG)
        except:
            pass

        # TODO: have to give raw text which is a mess, unless I can figure out better way to parse the script labels?
        # Doesn't look consistent across examples either :P :P
        return driver.page_source
