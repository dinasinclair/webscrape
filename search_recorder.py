from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from job_structs import QueryInfo
from constants import WAIT_SHORT, WAIT_LONG
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException
import time


class SearchRecorder:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.pagination_limit = 10
        self.current_search_page = None

    @staticmethod
    def return_error_query(query_text: str, location: str) -> QueryInfo:
        return QueryInfo.from_dict({'query_text': query_text,
                                    'location': location,
                                    'time': datetime.now(),
                                    'result_url': 'Error - query not completed.'})

    def make_query(self, query_text: str, location: str) -> QueryInfo:
        """
        Enters the job text and location text into the indeed search bar and presses enter.
        Args:
            query_text:
            location:

        Returns:
        """
        self.driver.get('https://www.indeed.com')
        self.driver.implicitly_wait(WAIT_LONG)

        # Enter input text into what/where search boxes
        try:
            job_text_box = self.driver.find_element_by_id('text-input-what')
            job_text_box.clear()
            job_text_box.send_keys(query_text)
        except NoSuchElementException:
            print("Could not find the query text box for query {}, {}.".format(query_text, location))
            return self.return_error_query(query_text, location)
        time.sleep(2)

        try:
            location_text_box = self.driver.find_element_by_id('text-input-where')
            location_text_box.clear()
            for i in range(1):
                location_text_box.send_keys(Keys.BACK_SPACE * 30)  # hacky fix because clear isn't working?
            location_text_box.send_keys(location)
        except NoSuchElementException:
            print("Could not find the location text box for query {}, {}.".format(query_text, location))
            return self.return_error_query(query_text, location)
        time.sleep(2)

        # Hit the find jobs button!
        try:
            find_jobs_button = self.driver.find_element_by_xpath('//button[text()="Find jobs"]')
            find_jobs_button.click()
        except NoSuchElementException:
            print("Could not find the find jobs button for query {}, {}.".format(query_text, location))
            return self.return_error_query(query_text, location)
        self.driver.implicitly_wait(WAIT_SHORT)

        query_info = QueryInfo.from_dict({'query_text': query_text,
                                          'location': location,
                                          'time': datetime.now(),
                                          'result_url': self.driver.current_url})
        return query_info

    @staticmethod
    def write_query_to_db(conn, query_info: QueryInfo) -> int:
        """

        Args:
            conn:
            query_info:

        Returns:

        """
        sql = ''' INSERT INTO queries(query_text, location, time, result_url)
                  VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (query_info.query_text,
                          query_info.location,
                          query_info.time,
                          query_info.result_url))
        return cur.lastrowid


if __name__ == "__main__":
    search_recorder = SearchRecorder()
    search_recorder.make_query('Software Engineer', 'New York, NY')
