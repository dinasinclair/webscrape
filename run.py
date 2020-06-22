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








class Orchestration:

    def __init__(self):
        self.search_recorder = SearchRecorder()
        self.job_recorder = JobRecorder()

    def run(self, query_text: str, location: str):
        # First, make the query and write the query info to the DB
        query_info = self.search_recorder.make_query(query_text, location)
        query_id = self.search_recorder.write_query_to_db(query_info)

        # Next, write the query job results to the DB
        self.job_recorder.write_all_jobs_to_db(query_info.result_url, conn, query_id)
