from sql_queries import create_queries_table, create_jobs_table
from run import Orchestration
from job_structs import QueryInfo, IndeedJobInfo
from datetime import datetime
from search_recorder import SearchRecorder
from job_recorder import JobRecorder
import pytest
import time


@pytest.fixture()
def query_info():
    query_info = QueryInfo.from_dict({'query_text': 'this is a query',
                                      'location': 'Canadia',
                                      'time': datetime.fromisoformat('2011-11-04'),
                                      'result_url': 'www.some_url'})
    return query_info


@pytest.fixture()
def malformed_query_info():
    query_info = QueryInfo.from_dict({'query_text': 'yay words',
                                      'location': 12345,
                                      'time': 'this is not a date!!!',
                                      'result_url': 'www.url.com'})
    return query_info


@pytest.fixture()
def job_info():
    job_info = IndeedJobInfo.from_dict({'title': 'ooh a title',
                                        'location': 'Portlandia',
                                        'company': 'Best Company Evah',
                                        'indeed_url': 'www.url.com',
                                        'page_number': 42,
                                        'rank_on_page': 234,
                                        'app_type': 'apply now',
                                        'company_url': 'company_url.com',
                                        'app_text': 'dang this some crazy s**t',
                                        'stats': {'a_stat': 17},
                                        'description': 'heya it a description'})
    return job_info


def test_create_queries_table(query_info):
    time.sleep(1)
    conn = Orchestration.create_db_connection('tests/test_db2.db')
    Orchestration.create_table(conn, create_queries_table)
    row = SearchRecorder.write_query_to_db(conn, query_info)
    assert row == 1
    time.sleep(1)
    row = SearchRecorder.write_query_to_db(conn, query_info)
    assert row == 2


def test_queries_table_write_fails_if_input_job_info(job_info):
    time.sleep(1)
    conn = Orchestration.create_db_connection('tests/test_db.db')
    Orchestration.create_table(conn, create_queries_table)
    with pytest.raises(AttributeError):
        SearchRecorder.write_query_to_db(conn, job_info)


def test_create_jobs_table(job_info):
    time.sleep(1)
    conn = Orchestration.create_db_connection('tests/test_db.db')
    Orchestration.create_table(conn, create_jobs_table)
    JobRecorder.write_job_to_db(conn=conn, job_info=job_info, query_id=5)


def test_jobs_table_write_fails_if_input_query_info(query_info):
    time.sleep(1)
    conn = Orchestration.create_db_connection('tests/test_db.db')
    Orchestration.create_table(conn, create_jobs_table)
    with pytest.raises(AttributeError):
        JobRecorder.write_job_to_db(conn, query_info, 42)


# Note: I'm not sure why this hits a type error?? I thought dataclasses
# don't do real time type checks.
def test_query_info_does_date_type_checking():
    with pytest.raises(TypeError):
        QueryInfo.from_dict({'query_text': 'yay words',
                             'location': 12345,
                             'time': 'this is not a date!!!',
                             'result_url': 'www.url.com'})
