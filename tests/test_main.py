import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.main import list_movies, get_movie, recommendations, query_endpoint
from app.schemas import QueryIn

def make_movie(**kw):
    defaults = {
        "id": 1, "title": "Inception", "year": 2010,
        "overview": None, "rating": 8.3,
        "genres": [SimpleNamespace(name="action")],
        "cast": None, "director": None,
    }
    defaults.update(kw)
    return SimpleNamespace(**defaults)

class FakeSession:
    def __init__(self, get_return=None, min_year=1900, max_year=2016):
        self._get_return = get_return
        self._min_year = min_year
        self._max_year = max_year

    def get(self, model, ident):
        return self._get_return

    class _One:
        def __init__(self, lo, hi): self.lo, self.hi = lo, hi
        def __iter__(self): return iter((self.lo, self.hi))
        def __getitem__(self, i): return (self.lo, self.hi)[i]

    class _Exec:
        def __init__(self, lo, hi): self.lo, self.hi = lo, hi
        def one(self): return FakeSession._One(self.lo, self.hi)

    def execute(self, *args, **kwargs):
        return FakeSession._Exec(self._min_year, self._max_year)

class TestEndpointsNoClient(unittest.TestCase):
    def test_get_movie_ok(self):
        db = FakeSession(get_return=make_movie(id=123))
        result = get_movie(movie_id=123, db=db)
        self.assertEqual(result.id, 123)

    def test_get_movie_not_found(self):
        from fastapi import HTTPException
        db = FakeSession(get_return=None)
        with self.assertRaises(HTTPException) as ctx:
            get_movie(movie_id=999, db=db)
        self.assertEqual(ctx.exception.status_code, 404)

    @patch("app.main.by_filters", return_value=[make_movie(id=1), make_movie(id=2)])
    def test_list_movies_uses_search(self, _mock):
        db = FakeSession()
        res = list_movies(genre=None, year=None, limit=2, db=db)
        self.assertEqual(len(res), 2)

    @patch("app.main.by_filters", return_value=[make_movie(id=1)])
    def test_recommendations_in_range(self, _mock):
        db = FakeSession(min_year=1990, max_year=2016)
        res = recommendations(genre=None, year=2010, limit=5, db=db)
        self.assertEqual(len(res), 1)

    @patch("app.search.by_filters", return_value=[])
    def test_recommendations_out_of_range(self, _mock):
        from fastapi import HTTPException
        db = FakeSession(min_year=1990, max_year=2016)
        with self.assertRaises(HTTPException) as ctx:
            recommendations(genre=None, year=2019, limit=5, db=db)
        self.assertEqual(ctx.exception.status_code, 400)

    @patch("app.llm.OpenAI")
    @patch("app.main.by_title", return_value=[make_movie(title="Inception")])
    def test_query_details_llm(self, _mock_by_title, MockOpenAI):
        # Fake response
        fake_choice = SimpleNamespace(message=SimpleNamespace(content="Summary"))
        fake_resp = SimpleNamespace(choices=[fake_choice])
        MockOpenAI.return_value = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=lambda **_: fake_resp)
            )
        )

        db = FakeSession()
        body = QueryIn(q="Tell me about Inception")
        out = query_endpoint(payload=body, db=db)
        self.assertEqual(out.intent, "details")
        self.assertEqual(out.results[0].title, "Inception")
        self.assertEqual(out.llm_response, "Summary")

if __name__ == "__main__":
    unittest.main(verbosity=2)