from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    username: str
    promts_left: int = 10

class SummarizerData(BaseModel):
    text: str
    max_length: int = 512