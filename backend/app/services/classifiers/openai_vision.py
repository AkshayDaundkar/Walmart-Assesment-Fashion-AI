import base64
import json
import logging
import re
from uuid import uuid4

import httpx

from app.core.config import settings
from app.schemas.library import AiAttributes
from app.services.model_output_parser import parse_model_output

logger = logging.getLogger(__name__)

_JSON_BLOCK = re.compile(r"\{[\s\S]*\}")


class OpenAiVisionClassifier:
    def __init__(self) -> None:
        if not settings.openai_api_key:
            msg = "openai_api_key is required when classifier_backend is openai"
            raise ValueError(msg)

    def classify_image(self, *, image_bytes: bytes, filename: str) -> tuple[str, AiAttributes]:
        b64 = base64.standard_b64encode(image_bytes).decode("ascii")
        mime = "image/jpeg"
        if filename.lower().endswith(".png"):
            mime = "image/png"
        if filename.lower().endswith(".webp"):
            mime = "image/webp"

        system = (
            "You are a senior fashion analyst. Respond with ONLY valid JSON, no markdown, "
            "matching this exact shape with snake_case keys: "
            '{"garment_type": str, "style": str, "material": str, "color_palette": [str], '
            '"pattern": str, "season": str, "occasion": str, "consumer_profile": str, '
            '"trend_notes": [str], "location_context": {"continent": str, "country": str, "city": str}, '
            '"time_context": {"year": int, "month": int, "season": str}}. '
            "Infer from the image; use Unknown when unsure."
        )

        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this garment photo and fill the JSON schema.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{b64}"},
                        },
                    ],
                },
            ],
            "max_tokens": 800,
        }

        last_error: Exception | None = None
        for attempt in range(settings.classification_max_retries):
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(
                        f"{settings.openai_base_url.rstrip('/')}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.openai_api_key}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    if isinstance(content, list):
                        text_parts: list[str] = []
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_parts.append(str(block.get("text", "")))
                        content = "".join(text_parts)
                    if not isinstance(content, str):
                        msg = "Unexpected OpenAI response shape"
                        raise ValueError(msg)
                    raw_json = _extract_json(content)
                    parsed = json.loads(raw_json)
                    attributes = parse_model_output(parsed)
                    description = (
                        f"{attributes.style} {attributes.garment_type.lower()} in "
                        f"{attributes.material.lower()} with {attributes.pattern.lower()} pattern."
                    )
                    return description, attributes
            except (httpx.HTTPError, json.JSONDecodeError, KeyError, ValueError) as exc:
                last_error = exc
                logger.warning("OpenAI classify attempt %s failed: %s", attempt + 1, exc)

        raise RuntimeError(f"Classification failed after retries: {last_error}") from last_error

    def next_id(self) -> str:
        return f"img_{uuid4().hex[:12]}"


def _extract_json(content: str) -> str:
    content = content.strip()
    if content.startswith("{"):
        return content
    match = _JSON_BLOCK.search(content)
    if match:
        return match.group(0)
    return content
