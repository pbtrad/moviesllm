import unittest
from types import SimpleNamespace
from app.search import by_title, by_filters

class _Scalars:
    def __init__(self, rows): self._rows = rows
    def all(self): return self._rows

class _Exec:
    def __init__(self, rows): self._rows = rows
    def scalars(self): return _Scalars(self._rows)

class FakeDB:
    def __init__(self, rows): self._rows = rows
    def execute(self, *_a, **_k): return _Exec(self._rows)

def m(**kw):
    d = dict(id=1, title="Inception", year=2010, overview=None, rating=8.3,
             genres=[SimpleNamespace(name="action")], cast=None, director=None)
    d.update(kw); return SimpleNamespace(**d)

class TestSearch(unittest.TestCase):
    def test_by_title_returns_rows(self):
        db = FakeDB([m(title="Inception")])
        out = by_title(db, "incep", limit=5)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].title, "Inception")

    def test_by_filters_basic(self):
        db = FakeDB([m(year=2010), m(year=2010)])
        out = by_filters(db, genre=None, year=2010, limit=10, order_by_rating=False)
        self.assertEqual(len(out), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)