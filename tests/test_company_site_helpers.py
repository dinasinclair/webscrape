import pytest
from selenium import webdriver
from company_site_helpers import CompanySiteParser
from constants import KEY_WORDS, WAIT_SHORT

HTML_SHORT = """<html><body>
<h1>Heading</h1>
<p>Paragraph.</p>
</body></html>"""

HTML_LONG = """<html><body>
<h1>Let's talk about gender identity!</h1>
<p>Do you indentify as non-binary? Nonbinary? cisgender? No problem!</p>
</body></html>"""


@pytest.fixture()
def driver():
    return webdriver.Chrome()


@pytest.fixture()
def zeroed_key_words_dict():
    stats_dict = {}
    for word in KEY_WORDS:
        stats_dict[word] = 0
    return stats_dict


class TestCompanySiteParser:

    def test_strip_html(self):
        stripped_html = CompanySiteParser.strip_html(HTML_SHORT)
        assert stripped_html == 'heading\tparagraph.'

    def test_html_to_stats_short(self, zeroed_key_words_dict):
        expected_dict = zeroed_key_words_dict
        stats_dict = CompanySiteParser.html_to_stats(HTML_SHORT)
        assert stats_dict == expected_dict

    def test_html_to_stats_long(self, zeroed_key_words_dict):
        expected_dict = zeroed_key_words_dict
        expected_dict['gender'] = 2
        expected_dict['non-binary'] = 1
        expected_dict['nonbinary'] = 1
        expected_dict['cisgender'] = 1
        stats_dict = CompanySiteParser.html_to_stats(HTML_LONG)
        assert stats_dict == expected_dict

    def test_get_lever_job_text(self, driver):
        driver.get(
            'https://jobs.lever.co/grabango/7ff6e367-6523-4ca2-b630-57a46881e467/apply?lever-source=Glassdoor')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_lever_job_text(driver)
        assert 'resume' in app_text
        driver.close()

    def test_get_lever_job_text_with_click(self, driver):
        driver.get(
            'https://jobs.lever.co/grabango/7ff6e367-6523-4ca2-b630-57a46881e467/apply?lever-source=Glassdoor')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_lever_job_text(driver)
        assert 'resume' in app_text
        driver.close()

    def test_get_greenhouse_job_text(self, driver):
        # TODO find a greenhouse example??
        pass

    def test_get_embedded_greenhouse_job_text(self, driver):
        driver.get(
            'https://www.docusign.com/company/careers/open?gh_jid=2179621&gh_src=678d46ab1us')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_embedded_greenhouse_job_text(driver)
        assert 'resume' in app_text
        driver.close()

    def test_get_embedded_lever_job_text(self, driver):
        driver.get(
            'https://scale.com/careers/ac8fc951-e58c-440c-96b3-402d43eab6df')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_embedded_lever_job_text(driver)
        assert 'resume' in app_text
        driver.close()

    def test_get_withgoogle_job_text(self, driver):
        driver.get(
            'https://hire.withgoogle.com/public/jobs/scottyai/view/P_AAAAAADAAADGmyZNJ2hxhI')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_withgoogle_job_text(driver)
        assert 'resume' in app_text

    def test_get_bamboohr_job_text(self, driver):
        driver.get(
            'https://aperiogroup.bamboohr.com/jobs/view.php?id=110&source=indeed&src=indeed&postedDate=2020-05-04')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_bamboohr_job_text(driver)
        assert 'resume' in app_text
        driver.close()

    def test_get_twitter_job_text(self, driver):
        driver.get(
            'https://careers.twitter.com/en/work-for-twitter/202005/staff-software-engineer-backend-tweet-services-.html')
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_twitter_job_text(driver)
        assert 'transgender' in app_text

    def test_get_facebook_job_text(self, driver):
        driver.get("https://www.facebook.com/careers/jobs/264448864681295/?ref=a8lA00000004CJ6IAM")
        driver.implicitly_wait(WAIT_SHORT)
        app_text = CompanySiteParser.get_facebook_job_text(driver)
        assert 'contact information' in app_text
        driver.close()


'''
what do I want as a test?
given link, can I
(a) identify correct app type

so code structure should be
(1) get_job_type(link) --> app_type: str
'''
