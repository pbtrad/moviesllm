from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MovieOut(BaseModel):
    id: int
    title: str
    year: Optional[int] = None
    overview: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = []
    cast: Optional[str] = None
    director: Optional[str] = None


class QueryIn(BaseModel):
    q: str


class QueryOut(BaseModel):
    intent: str
    filters: Dict[str, Any]
    results: List[MovieOut]
    llm_response: str