from fastapi import FastAPI, HTTPException
from datetime import datetime
import json

from app.models import CaseTask
from app.db import get_conn
from app.orchestration import (
    build_idempotency_key,
    load_case,
    get_or_create_decision,
    guardrails,
)
from app.mock_backend import call_partner_api

app = FastAPI(title="AI Assisted Case Orchestrator")

@app.post("/case-task")
def process_case(task: CaseTask):
    key = build_idempotency_key(task.case_id, task.description)

    case_row = load_case(task.case_id)
    if not case_row:
        raise HTTPException(status_code=404, detail="Case not found")

    decision = get_or_create_decision(task.dict(), case_row, key)

    allowed = guardrails(case_row, decision)

    if not allowed:
        outcome = "MANUAL"
    else:
        success = call_partner_api()
        outcome = "AUTO_SUCCESS" if success else "AUTO_FAILED"

    # Audit log
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_log(case_id,outcome,intent,route_target,confidence,created_at) VALUES (?,?,?,?,?,?)",
        (
            task.case_id,
            outcome,
            decision.get("intent"),
            decision.get("routeTarget"),
            float(decision.get("confidence", 0.0)),
            datetime.utcnow().isoformat()
        )
    )
    conn.commit()
    conn.close()

    return {"outcome": outcome, "decision": decision, "idempotencyKey": key}

@app.get("/audit/{case_id}")
def get_audit(case_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, case_id, outcome, intent, route_target, confidence, created_at FROM audit_log WHERE case_id=? ORDER BY id DESC",
        (case_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return {"case_id": case_id, "entries": rows}