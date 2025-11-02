import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models import Base, Movie, Genre

class TestModelsMapping(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

    def test_movie_genre_relationship(self):
        db = self.Session()
        try:
            g = Genre(name="action"); db.add(g); db.flush()
            m = Movie(title="Inception", year=2010, rating=8.3)
            m.genres.append(g)
            db.add(m); db.commit()

            out = db.query(Movie).first()
            self.assertEqual(out.title, "Inception")
            self.assertEqual([x.name for x in out.genres], ["action"])
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)