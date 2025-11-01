# api/schemas.py
from pydantic import BaseModel

class IngestResponse(BaseModel):
    status: str
    message: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    sources: list = []
    # could add sources here in the future