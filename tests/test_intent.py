import unittest
from app.intent import parse_query

class TestIntent(unittest.TestCase):
    def test_details(self):
        intent, fields = parse_query("Tell me about Inception")
        self.assertEqual(intent, "details")
        self.assertEqual(fields["title"].lower(), "inception")

    def test_recommend_with_year(self):
        intent, fields = parse_query("recommend action movies from 2014")
        self.assertEqual(intent, "recommend")
        self.assertEqual(fields["genre"], "action")
        self.assertEqual(fields["year"], 2014)

    def test_fallback(self):
        intent, fields = parse_query("random text")
        self.assertEqual(intent, "search")
        self.assertEqual(fields["text"], "random text")

if __name__ == "__main__":
    unittest.main()