import pytest
from job_recorder import JobRecorder
from constants import ALL_MLE_SEA_URL

HTML_SHORT = """<html><body>
<h1>Heading</h1>
<p>Paragraph.</p>
</body></html>"""

HTML_LONG = """<html><body>
<h1>Let's talk about gender identity!</h1>
<p>Do you indentify as non-binary? Nonbinary? cisgender? No problem!</p>
</body></html>"""


def test_job_recorder():
    job_recorder = JobRecorder()
    job_recorder.current_search_page = ALL_MLE_SEA_URL
    assert job_recorder.pagination_limit == 10


def test_next_page_exists():
    job_recorder = JobRecorder()
    job_recorder.driver.get(ALL_MLE_SEA_URL)
    assert job_recorder.next_page_exists()
    job_recorder.driver.close()


'''
what do I want as a test?
given link, can I
(a) identify correct app type
(b) given app type, link, get correct text

so code structure should be
(1) get_job_type(link) --> app_type: str
(2) get_job_text(app_type

'''
