import re
from typing import Literal

Intent = Literal["details", "recommend", "top", "search"]


def parse_query(q) -> tuple[Intent, dict]:
    q_l = q.lower().strip()

    # details search "tell me about ...", "details for ..."
    m = re.search(r"(tell me about|details? (on|for))\s+(?P<title>.+)", q_l)
    if m:
        return "details", {"title": m.group("title").strip()}

    # recommend search "recommend action movies from 2014"
    m = re.search(
        r"recommend\s+(?P<genre>\w+)\s+movies(?:\s+from\s+(?P<year>\d{4}))?",
        q_l,
    )
    if m:
        return "recommend", {
            "genre": m.group("genre"),
            "year": int(m.group("year")) if m.group("year") else None,
        }

    # top search "top rated sci-fi from 2010", "best comedy 1999"
    m = re.search(
        r"(top|best)\s+(?P<genre>\w+)?\s*(?:from\s+)?(?P<year>\d{4})?",
        q_l,
    )
    if m and (m.group("genre") or m.group("year")):
        return "top", {
            "genre": m.group("genre"),
            "year": int(m.group("year")) if m.group("year") else None,
        }

    # fallback search
    return "search", {"text": q_l}