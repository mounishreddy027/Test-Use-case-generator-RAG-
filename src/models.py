from pydantic import BaseModel
from typing import List, Literal, Optional

class TestCase(BaseModel):
    id: str
    title: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    type: Literal["Positive", "Negative", "Boundary"]

class TestSuite(BaseModel):
    type: str
    feature: str
    objective: str
    test_cases: List[TestCase]
    missing_info: List[str]
    assumptions: List[str]