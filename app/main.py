from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import structlog

from .db import get_db, engine
from .models import Base, Movie
from .schemas import MovieOut, QueryIn, QueryOut
from .intent import parse_query
from .search import by_title, by_filters
from .llm import summarize_with_llm

log = structlog.get_logger(__name__)
app = FastAPI(title="Movies LLM API", version="0.1.0")

Base.metadata.create_all(bind=engine)

def serialize_movie(m: Movie) -> MovieOut:
    return MovieOut(
        id=m.id,
        title=m.title,
        year=m.year,
        overview=m.overview,
        rating=m.rating,
        genres=[g.name for g in (m.genres or [])],
        cast=m.cast,
        director=m.director,
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/movies", response_model=list[MovieOut])
def list_movies(
    genre: str | None = Query(default=None),
    year: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    movies = by_filters(db, genre=genre, year=year, limit=limit)
    return [serialize_movie(m) for m in movies]


@app.get("/movies/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    m = db.get(Movie, movie_id)
    if not m:
        raise HTTPException(404, "Movie not found")
    return serialize_movie(m)


@app.get("/recommendations", response_model=list[MovieOut])
def recommendations(
    genre: str | None = Query(default=None),
    year: int | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    if year is not None:
        min_year, max_year = db.execute(
            select(func.min(Movie.year), func.max(Movie.year))
        ).one()
        if min_year is not None and max_year is not None:
            if year < min_year or year > max_year:
                raise HTTPException(
                    status_code=400,
                    detail=f"Year {year} is outside available range {min_year}-{max_year}.",
                )

    movies = by_filters(db, genre=genre, year=year, limit=limit, order_by_rating=True)
    return [serialize_movie(m) for m in movies]


@app.post("/query", response_model=QueryOut)
def query_endpoint(payload: QueryIn, db: Session = Depends(get_db)):
    intent, filters = parse_query(payload.q)

    if intent == "details" and filters.get("title"):
        movies = by_title(db, filters["title"], limit=5)
    elif intent == "recommend":
        movies = by_filters(
            db,
            genre=filters.get("genre"),
            year=filters.get("year"),
            limit=10,
            order_by_rating=True,
        )
    elif intent == "top":
        movies = by_filters(
            db,
            genre=filters.get("genre"),
            year=filters.get("year"),
            limit=10,
            order_by_rating=True,
        )
    else:
        movies = by_title(db, filters.get("text", ""), limit=10)

    results = [serialize_movie(m) for m in movies]

    context = {"movies": [r.model_dump() for r in results]}
    llm_resp = summarize_with_llm(context, payload.q)

    return QueryOut(
        intent=intent,
        filters=filters,
        results=results,
        llm_response=llm_resp,
    )