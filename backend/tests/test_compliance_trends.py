from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.compliance_result import ComplianceResult
from .helpers import ADMIN_PASSWORD, ADMIN_USERNAME

client = TestClient(app)


def _login_admin() -> str:
    resp = client.post("/auth/login", data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200
    payload = resp.json()
    token = payload.get("access_token")
    assert token
    return token


def _seed_results():
    session = SessionLocal()
    now = datetime.utcnow()
    try:
        session.query(ComplianceResult).delete()
        session.add_all(
            [
                ComplianceResult(
                    tenant_id=1,
                    module="cis_benchmark",
                    status="pass",
                    recorded_at=now - timedelta(days=1),
                    details="nightly scan",
                ),
                ComplianceResult(
                    tenant_id=1,
                    module="cis_benchmark",
                    status="fail",
                    recorded_at=now - timedelta(days=2),
                    details="control drift",
                ),
                ComplianceResult(
                    tenant_id=1,
                    module="pci_dss_check",
                    status="pass",
                    recorded_at=now - timedelta(days=3),
                    details="pci baseline",
                ),
            ]
        )
        session.commit()
    finally:
        session.close()


def test_trend_insights_returns_summary_and_trend():
    token = _login_admin()
    _seed_results()

    resp = client.get(
        "/compliance/trends/insights?days=7",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()

    summary = body.get("summary")
    trend = body.get("trend")

    assert isinstance(trend, list)
    assert len(trend) == 7
    assert summary is not None
    assert 0 <= summary["coverage"] <= 100
    assert summary["open_failures"] >= 0
    assert isinstance(summary["net_change"], (int, float))
