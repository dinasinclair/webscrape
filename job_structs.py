from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from typing import List, Dict

@dataclass_json
@dataclass
class IndeedJobInfo:
    title: str
    company: str
    location: str
    indeed_url: str
    page_number: int
    app_type: str
    app_text: str
    company_url: str
    stats: Dict[str, int]
    rank_on_page: int
    description: str = None  # TODO: make not none, collect during get()


@dataclass_json
@dataclass
class CompanySiteInfo:
    app_type: str
    app_text: str
    app_url: str
    stats: Dict = None


@dataclass_json
@dataclass
class QueryInfo:
    query: str
    location: str
    time: datetime
    result: List[IndeedJobInfo]