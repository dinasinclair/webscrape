"""
TODO: This is where we'll actually run the search queries, pass
"""

from job_structs import QueryInfo, IndeedJobInfo
from SearchRecorder import SearchRecorder
from JobRecorder import JobRecorder


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
