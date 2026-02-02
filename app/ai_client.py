import json
from openai import OpenAI
from openai import RateLimitError

client = OpenAI()

SYSTEM_PROMPT = """
You are an AI assistant for case processing.

Return ONLY valid JSON matching this schema exactly:

{
  "intent": "RETRY_EXTERNAL_CALL|MANUAL_REVIEW|ESCALATE",
  "nextStep": "AUTOMATED_EXECUTION|MANUAL_REVIEW",
  "routeTarget": "PARTNER_API|CORE_SYSTEM",
  "retryStrategy": "NONE|IMMEDIATE|BACKOFF",
  "riskScore": 0.0,
  "confidence": 0.0,
  "reasonCode": "TRANSIENT_TIMEOUT_PATTERN|VALIDATION_ERROR|UNKNOWN"
}

No extra keys. No markdown. No comments.
"""

def get_ai_decision(payload: dict) -> dict:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": json.dumps(payload)}
            ],
            temperature=0,
        )

        content = resp.choices[0].message.content
        return json.loads(content)

    except RateLimitError:
        # ---- Fallback decision when AI is unavailable ----
        # This keeps orchestration alive and proves your design
        return {
            "intent": "MANUAL_REVIEW",
            "nextStep": "MANUAL_REVIEW",
            "routeTarget": "CORE_SYSTEM",
            "retryStrategy": "NONE",
            "riskScore": 0.9,
            "confidence": 0.0,
            "reasonCode": "AI_UNAVAILABLE"
        }