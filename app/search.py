from sqlalchemy import select, func
from sqlalchemy.orm import Session
from .models import Movie, Genre


def by_title(db: Session, title_like: str, limit: int = 10):
    stmt = (
        select(Movie)
        .where(func.lower(Movie.title).like(f"%{title_like.lower()}%"))
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()


def by_filters(
    db: Session,
    genre: str | None = None,
    year: int | None = None,
    limit: int = 10,
    order_by_rating: bool = False,
):
    stmt = select(Movie)

    if year:
        stmt = stmt.where(Movie.year == year)

    if genre:
        stmt = (
            stmt.join(Movie.genres)
            .where(func.lower(Genre.name) == genre.lower())
        )

    if order_by_rating:
        stmt = stmt.order_by(Movie.rating.desc().nullslast())

    stmt = stmt.limit(limit)
    return db.execute(stmt).scalars().all()