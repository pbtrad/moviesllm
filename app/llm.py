import json
import structlog
from openai import OpenAI
from .settings import settings

log = structlog.get_logger(__name__)


def summarize_with_llm(context: dict, prompt: str) -> str:
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        system_prompt = (
            "You are a helpful movie expert. Answer concisely. "
            "Use the provided data truthfully; if missing, say so."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Data:\n{json.dumps(context, indent=2)}\n\n"
                           f"Question:\n{prompt}",
            },
        ]

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        log.warning("llm_fallback", error=str(e))
        return (
            "LLM unavailable. Here’s the structured data I found:\n"
            + json.dumps(context, indent=2)
        )