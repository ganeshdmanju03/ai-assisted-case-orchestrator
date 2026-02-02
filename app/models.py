from pydantic import BaseModel

class CaseTask(BaseModel):
    case_id: str
    description: str
    channel: str
    user_role: str


class AIDecision(BaseModel):
    intent: str
    nextStep: str
    routeTarget: str
    retryStrategy: str
    riskScore: float
    confidence: float
    reasonCode: str
