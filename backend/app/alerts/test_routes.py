from fastapi import APIRouter, Depends
from app.alerts.handlers import send_compliance_failure_alert
from datetime import datetime

router = APIRouter(prefix="/alerts/test", tags=["Alerts Test"])

@router.post("/compliance-failure")
def simulate_failure_alert(email: str = "admin@tenantra.com"):
    module = "Windows Patch Scanner"
    agent = "Agent-001"
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    success = send_compliance_failure_alert(email, module, agent, timestamp)
    return {"email_sent": success}
