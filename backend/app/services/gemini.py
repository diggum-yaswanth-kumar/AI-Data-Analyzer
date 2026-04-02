import json
import re
import time
from typing import Any

import requests

from app.config import get_settings


class GeminiService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _extract_json(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(cleaned[start : end + 1])
        raise ValueError("Gemini returned a non-JSON response.")

    def _post(self, prompt: str) -> dict[str, Any]:
        if not self.settings.gemini_api_key:
            raise RuntimeError("Gemini API key is not configured.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.gemini_model}:generateContent?key={self.settings.gemini_api_key}"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1400,
                "responseMimeType": "application/json",
            },
        }
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = requests.post(url, json=payload, timeout=45)
                response.raise_for_status()
                break
            except requests.HTTPError as exc:
                last_error = exc
                status_code = exc.response.status_code if exc.response is not None else None
                if status_code == 429 and attempt < 2:
                    time.sleep(1.2 * (attempt + 1))
                    continue
                raise
        else:
            raise last_error or RuntimeError("Gemini request failed.")

        body = response.json()
        candidates = body.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini did not return any candidates.")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise RuntimeError("Gemini response was empty.")
        return self._extract_json(text)

    def generate_analysis(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = f"""
You are an expert data analyst for a SaaS analytics dashboard.
Return strict JSON with the shape:
{{
  "summary": "short executive summary",
  "patterns": ["pattern 1", "pattern 2", "pattern 3"],
  "anomalies": ["anomaly 1", "anomaly 2"],
  "business_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
  "recommended_questions": ["question 1", "question 2", "question 3"]
}}

Use only the supplied dataset profile. Be concise, practical, and business-focused.
Dataset profile:
{json.dumps(payload, indent=2, default=str)}
"""
        return self._post(prompt)

    def answer_question(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = f"""
You are answering a user's natural language question about a dataset.
Return strict JSON with:
{{
  "answer": "clear answer",
  "reasoning": "brief explanation grounded in the provided stats",
  "follow_up": ["follow up 1", "follow up 2"]
}}

Context:
{json.dumps(payload, indent=2, default=str)}
"""
        return self._post(prompt)


gemini_service = GeminiService()
