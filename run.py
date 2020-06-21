"""
TODO: This is where we'll actually run the search queries, pass
"""

from job_structs import QueryInfo, IndeedJobInfo
from search_recorder import SearchRecorder
from job_recorder import JobRecorder
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def write_query_to_db(conn, query_info: QueryInfo):
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


def create_task(conn, job_info: IndeedJobInfo, query_id: int):
    """

    Args:
        conn: 
        job_info:

    Returns:

    """
    sql = ''' INSERT INTO tasks(query_id, \
                                app_type, \
                                app_text, \
                                company, \
                                title, \
                                description, \
                                company_url, \
                                indeed_url, \
                                page_number, \
                                rank_on_page)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (
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
    return cur.lastrowid


class Orchestration:

    def __init__(self):
        self.search_recorder = SearchRecorder()
        self.job_recorder = JobRecorder()

    def run(self, query_text: str, location: str):
        # First, make the query and write the query info to the DB
        query_info = self.search_recorder.make_query(query_text, location)
        query_id = self.search_recorder.write_query_to_db(query_info)

        # Next, write the query job results to the DB
        self.job_recorder.get_all_job_info(query_info.result_url, "pretend_file_until_I_pass_in_query_ID")
