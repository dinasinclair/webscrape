from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from typing import List, Dict

@dataclass_json
@dataclass
class JobInfo:
    title: str
    company: str
    location: str
    indeed_url: str
    page_number: int
    app_type: str = None
    app_text: str = None
    company_url: str = None
    rank: int = None
    description: str = None  # TODO: make not none, collect during get()
    stats: Dict = None


@dataclass_json
@dataclass
class QueryInfo:
    query: str
    location: str
    time: datetime
    result: List[JobInfo]