from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Text, ForeignKey, Table, Column


class Base(DeclarativeBase):
    pass


movie_genre = Table(
    "movie_genre",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(400), index=True)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    overview: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float | None] = mapped_column(Float)
    cast: Mapped[str | None] = mapped_column(Text)
    director: Mapped[str | None] = mapped_column(String(200))

    genres: Mapped[list["Genre"]] = relationship(
        "Genre",
        secondary=movie_genre,
        back_populates="movies",
        lazy="selectin",
    )


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    movies: Mapped[list[Movie]] = relationship(
        "Movie",
        secondary=movie_genre,
        back_populates="genres",
        lazy="selectin",
    )