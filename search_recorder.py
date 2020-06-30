from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from job_structs import QueryInfo
from constants import WAIT_SHORT, WAIT_LONG, VERSION
from datetime import datetime
from sql_queries import insert_into_queries_table

from selenium.common.exceptions import NoSuchElementException
import time
import sqlite3


class SearchRecorder:

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
        driver = webdriver.Chrome()
        driver.get('https://www.indeed.com')
        driver.implicitly_wait(WAIT_LONG)

        # Enter input text into what/where search boxes
        try:
            job_text_box = driver.find_element_by_id('text-input-what')
            job_text_box.clear()
            job_text_box.send_keys(query_text)
        except NoSuchElementException:
            print("Could not find the query text box for query {}, {}.".format(query_text, location))
            return self.return_error_query(query_text, location)
        time.sleep(2)

        try:
            location_text_box = driver.find_element_by_id('text-input-where')
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
            find_jobs_button = driver.find_element_by_xpath('//button[text()="Find jobs"]')
            find_jobs_button.click()
        except NoSuchElementException:
            print("Could not find the find jobs button for query {}, {}.".format(query_text, location))
            return self.return_error_query(query_text, location)
        driver.implicitly_wait(WAIT_SHORT)

        # Find the total number of job hits!
        try:
            num_hits_elem = driver.find_element_by_id('searchCountPages')
            num_hits_text_list = num_hits_elem.text.split()
            if len(num_hits_text_list) != 5:
                print("Num hits text not in expected format. Found: ", num_hits_text_list)
            print("as a list: ", num_hits_text_list)
            total_hits = num_hits_text_list[3].replace(",", "")
            print("Total hits: ", total_hits)
        except NoSuchElementException:
            total_hits = None

        query_info = QueryInfo.from_dict({'scraper_version': VERSION,
                                          'query_text': query_text,
                                          'location': location,
                                          'time': datetime.now(),
                                          'result_url': driver.current_url,
                                          'total_hits': total_hits})
        driver.close()
        return query_info

    @staticmethod
    def write_query_to_db(conn, query_info: QueryInfo) -> int:
        """

        Args:
            conn:
            query_info:

        Returns:

        """
        cur = conn.cursor()
        cur.execute(insert_into_queries_table, (query_info.scraper_version,
                                                query_info.query_text,
                                                query_info.location,
                                                query_info.time,
                                                query_info.result_url,
                                                query_info.total_hits))
        return cur.lastrowid


if __name__ == "__main__":
    search_recorder = SearchRecorder()
    search_recorder.make_query('Software Engineer', 'New York, NY')
