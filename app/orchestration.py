import json
import hashlib
from datetime import datetime
from app.db import get_conn
from app.ai_client import get_ai_decision

def build_idempotency_key(case_id: str, description: str) -> str:
    raw = case_id.strip() + "|" + description.lower().strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def load_case(case_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT case_id, state, retry_count, last_error_type, priority FROM cases WHERE case_id=?", (case_id,))
    row = cur.fetchone()
    conn.close()
    return row

def load_ai_decision(key: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT decision_json FROM ai_decisions WHERE idempotency_key=?", (key,))
    row = cur.fetchone()
    conn.close()
    return row

def store_ai_decision(key: str, decision: dict, model: str = "gpt-4o-mini"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ai_decisions(idempotency_key, decision_json, model, created_at) VALUES (?,?,?,?)",
        (key, json.dumps(decision), model, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def guardrails(case_row, decision: dict) -> bool:
    # case_row = (case_id, state, retry_count, last_error_type, priority)
    state = case_row[1]
    retry_count = case_row[2]

    if decision.get("confidence", 0) < 0.80:
        return False
    if decision.get("riskScore", 1) > 0.30:
        return False
    if state != "OPEN":
        return False
    if retry_count >= 3:
        return False

    # Ensure intent is one we allow for auto exec
    if decision.get("intent") != "RETRY_EXTERNAL_CALL":
        return False
    if decision.get("nextStep") != "AUTOMATED_EXECUTION":
        return False

    return True

def build_ai_payload(task_dict: dict, case_row):
    return {
        "task": task_dict,
        "caseContext": {
            "caseState": case_row[1],
            "retryCount": case_row[2],
            "lastErrorType": case_row[3],
            "priority": case_row[4],
        }
    }

def get_or_create_decision(task_dict: dict, case_row, idempotency_key: str) -> dict:
    cached = load_ai_decision(idempotency_key)
    if cached:
        return json.loads(cached[0])

    payload = build_ai_payload(task_dict, case_row)
    decision = get_ai_decision(payload)
    store_ai_decision(idempotency_key, decision)
    return decision