# tests/test_llm_unittest.py
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.llm import summarize_with_llm


class TestLLM(unittest.TestCase):
    @patch("app.llm.OpenAI")
    def test_summarize_success(self, MockOpenAI):
        # Fake OpenAI response
        fake_resp = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Summary"))]
        )
        MockOpenAI.return_value = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=lambda **_: fake_resp)
            )
        )

        result = summarize_with_llm({"movies": [{"title": "Kingpin"}]}, "Tell me about Kingpin")
        self.assertEqual(result, "Summary")

    @patch("app.llm.OpenAI", side_effect=Exception("API connection failed"))
    def test_summarize_fallback(self, _MockOpenAI):
        context = {"key": "value"}
        result = summarize_with_llm(context, "hi")
        self.assertIn("LLM unavailable", result)
        self.assertIn('"key": "value"', result)


if __name__ == "__main__":
    unittest.main(verbosity=2)