Here is a ready-to-copy README.md for your repository.

Just copy everything below and paste it into a file called README.md in your project root.

⸻

AI-Assisted Case Orchestrator

This repository contains a small reference implementation that demonstrates how an AI model can be integrated into an enterprise-style backend flow as a recommendation component, while keeping execution deterministic, auditable and safe.

The service exposes a simple case-processing API where an LLM is used only to recommend the next step and routing based on contextual information and execution history.
All execution decisions are enforced by deterministic guardrails.

⸻

What problem this project addresses

Many AI agent architectures allow the model to directly control tools and execution flow.

This project intentionally explores a safer design:
	•	the AI recommends
	•	the orchestration layer validates
	•	the orchestration layer executes

The goal is to show how AI can be embedded into an integration or workflow pipeline without breaking operational guarantees such as idempotency, replayability and auditability.

⸻

## High-level flow

- API request  
- Deterministic validation  
- Load case context  
- AI recommendation (structured JSON only)  
- Persist AI decision (idempotency)  
- Deterministic guardrails  
- Execute backend call or route to manual review  
- Audit log


Design principles

This project follows three strict architectural rules:
	1.	The AI model never executes backend actions.
	2.	The AI output must follow a strict JSON contract.
	3.	The final execution path is always decided by deterministic logic.

⸻

Why AI is used here

AI is used only where the problem is interpretation, not control flow.
Typical examples include:
	•	classifying intent from free-text task descriptions
	•	recommending the next processing step
	•	suggesting a routing target
	•	providing a risk or anomaly signal

If a decision can be derived purely from structured data and stable business rules, it should be implemented using deterministic logic instead of an AI model.

⸻

Reliability and fallback

External AI calls are treated as unreliable dependencies.

If the AI call fails (for example due to quota limits, rate limiting, network issues or invalid responses), the service produces a conservative fallback decision and routes the case to manual review.

This allows the orchestration flow to remain operational and auditable even when AI is unavailable.

⸻

Technology stack
	•	Python
	•	FastAPI
	•	SQLite
	•	OpenAI API (optional – graceful fallback is implemented)

⸻

Setup

Create a virtual environment

     python3 -m venv .venv
     source .venv/bin/activate   

Install dependencies
    pip install -r requirements.txt

Create the database
    sqlite3 app.db < init_db.sql

Insert one sample case:
    sqlite3 app.db "INSERT INTO cases VALUES ('C1001','OPEN',1,'TIMEOUT','MEDIUM');"

Configuration

Set the OpenAI API key (optional – the service supports fallback if it is not available):
    export OPENAI_API_KEY="your_api_key"

Run the service
    http://127.0.0.1:8000/docs

Example request
    POST /case-task

        {
    "case_id": "C1001",
    "description": "Partner API failed again with timeout, please retry for policy 4711",
    "channel": "SYSTEM",
    "user_role": "OPS"
    }

What to observe
	•	The AI decision is persisted using an idempotency key.
	•	Retrying the same request does not invoke the model again.
	•	Guardrails decide whether execution is allowed.
	•	When the AI call is unavailable, the flow degrades safely to manual review.

⸻

Scope and limitations

This project is intentionally small and focuses only on architectural boundaries between:
	•	probabilistic reasoning (AI recommendations)
	•	deterministic orchestration and execution

It is not intended to be a production-ready framework, but a reference implementation for experimenting with AI-assisted orchestration patterns.
