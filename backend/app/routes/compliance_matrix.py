"""Extended compliance matrix endpoints."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.compliance_framework import ComplianceFramework
from app.models.compliance_rule import ComplianceRule, ComplianceRuleFramework
from app.models.user import User
from app.schemas.compliance import (
    ComplianceFrameworkCreate,
    ComplianceFrameworkRead,
    ComplianceMatrixResponse,
    ComplianceRuleCreate,
    ComplianceRuleRead,
)

router = APIRouter(prefix="/compliance-matrix", tags=["Compliance"])


def _ensure_admin(user: User) -> None:
    if user.role not in {"admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Administrative access required")


@router.get("/frameworks", response_model=List[ComplianceFrameworkRead])
def list_frameworks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ComplianceFrameworkRead]:
    _ensure_admin(current_user)
    frameworks = db.query(ComplianceFramework).order_by(ComplianceFramework.name.asc()).all()
    return [ComplianceFrameworkRead.from_orm(framework) for framework in frameworks]


@router.post("/frameworks", response_model=ComplianceFrameworkRead, status_code=201)
def create_framework(
    payload: ComplianceFrameworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplianceFrameworkRead:
    _ensure_admin(current_user)
    existing = db.query(ComplianceFramework).filter(ComplianceFramework.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=409, detail="Framework code already exists")
    framework = ComplianceFramework(
        name=payload.name,
        code=payload.code.upper(),
        description=payload.description,
        category=payload.category,
    )
    db.add(framework)
    db.commit()
    db.refresh(framework)
    return ComplianceFrameworkRead.from_orm(framework)


@router.get("/rules", response_model=List[ComplianceRuleRead])
def list_rules(
    framework_id: Optional[int] = Query(None, description="Filter by framework"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ComplianceRuleRead]:
    _ensure_admin(current_user)
    query = db.query(ComplianceRule)
    if framework_id is not None:
        query = (
            query.join(ComplianceRuleFramework)
            .filter(ComplianceRuleFramework.framework_id == framework_id)
        )
    rules = query.order_by(ComplianceRule.control_id.asc()).all()
    response: List[ComplianceRuleRead] = []
    for rule in rules:
        framework_ids = [link.framework_id for link in rule.framework_links]
        response.append(
            ComplianceRuleRead(
                id=rule.id,
                control_id=rule.control_id,
                title=rule.title,
                description=rule.description,
                category=rule.category,
                service_area=rule.service_area,
                framework_ids=framework_ids,
            )
        )
    return response


@router.post("/rules", response_model=ComplianceRuleRead, status_code=201)
def create_rule(
    payload: ComplianceRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplianceRuleRead:
    _ensure_admin(current_user)
    existing = db.query(ComplianceRule).filter(ComplianceRule.control_id == payload.control_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Control already exists")
    rule = ComplianceRule(
        control_id=payload.control_id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        service_area=payload.service_area,
    )
    db.add(rule)
    db.flush()
    for idx, framework_id in enumerate(payload.framework_ids or []):
        framework = db.query(ComplianceFramework).filter(ComplianceFramework.id == framework_id).first()
        if not framework:
            raise HTTPException(status_code=404, detail=f"Framework {framework_id} not found")
        db.add(
            ComplianceRuleFramework(
                rule_id=rule.id,
                framework_id=framework_id,
                reference=(payload.references or [None])[idx] if payload.references and idx < len(payload.references) else None,
            )
        )
    db.commit()
    db.refresh(rule)
    framework_ids = [link.framework_id for link in rule.framework_links]
    return ComplianceRuleRead(
        id=rule.id,
        control_id=rule.control_id,
        title=rule.title,
        description=rule.description,
        category=rule.category,
        service_area=rule.service_area,
        framework_ids=framework_ids,
    )


@router.get("/matrix", response_model=ComplianceMatrixResponse)
def compliance_matrix(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplianceMatrixResponse:
    _ensure_admin(current_user)
    frameworks = db.query(ComplianceFramework).order_by(ComplianceFramework.name.asc()).all()
    rules = db.query(ComplianceRule).order_by(ComplianceRule.control_id.asc()).all()
    return ComplianceMatrixResponse(
        frameworks=[ComplianceFrameworkRead.from_orm(fw) for fw in frameworks],
        rules=[
            ComplianceRuleRead(
                id=rule.id,
                control_id=rule.control_id,
                title=rule.title,
                description=rule.description,
                category=rule.category,
                service_area=rule.service_area,
                framework_ids=[link.framework_id for link in rule.framework_links],
            )
            for rule in rules
        ],
    )
