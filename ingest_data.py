import csv
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.db import engine
from app.models import Base, Movie, Genre
import structlog

log = structlog.get_logger(__name__)


def ensure_genre(session: Session, name: str) -> Genre:
    g = session.query(Genre).filter(Genre.name == name).one_or_none()
    if g:
        return g
    g = Genre(name=name)
    session.add(g)
    session.flush()
    return g


def load_tmdb_data(movies_csv: Path, credits_csv: Path, limit: int | None = None):
    Base.metadata.create_all(bind=engine)
    from sqlalchemy.orm import sessionmaker

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    credits_map = {}
    with credits_csv.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for i, row in enumerate(r):
            cid = int(row["movie_id"])
            cast = []
            try:
                cast_data = json.loads(row["cast"])
                cast = [c["name"] for c in cast_data[:10]]
            except Exception:
                cast = []

            director = None
            try:
                crew_data = json.loads(row["crew"])
                for c in crew_data:
                    if c.get("job") == "Director":
                        director = c.get("name")
                        break
            except Exception:
                pass
            credits_map[cid] = {"cast": cast, "director": director}

    with movies_csv.open(newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)

        session = SessionLocal()
        try:
            for i, row in enumerate(r):
                if limit and i >= limit:
                    break

                mid = int(row["id"])
                title = row["title"].strip()
                overview = row.get("overview") or None
                try:
                    year = int(row.get("release_date", "")[:4]) if row.get(
                        "release_date"
                    ) else None
                except Exception:
                    year = None

                try:
                    vote_avg = float(row.get("vote_average")) \
                        if row.get("vote_average") else None
                except Exception:
                    vote_avg = None

                m = Movie(
                    id=mid,
                    title=title,
                    year=year,
                    overview=overview,
                    rating=vote_avg,
                )

                # genres
                try:
                    gdata = json.loads(row["genres"])
                except Exception:
                    gdata = []
                for g in gdata:
                    gname = g.get("name")
                    if not gname:
                        continue
                    gobj = ensure_genre(session, gname)
                    m.genres.append(gobj)

                # credits
                creds = credits_map.get(mid, {})
                cast_list = creds.get("cast") or []
                m.cast = "|".join(cast_list) if cast_list else None
                m.director = creds.get("director")

                session.add(m)

                if i % 500 == 0:
                    session.commit()
                    log.info("ingested", count=i)

            session.commit()
            log.info("done")
        finally:
            session.close()


if __name__ == "__main__":
    data_dir = Path("./data")
    load_tmdb_data(
        data_dir / "tmdb_5000_movies.csv",
        data_dir / "tmdb_5000_credits.csv",
        limit=None,
    )