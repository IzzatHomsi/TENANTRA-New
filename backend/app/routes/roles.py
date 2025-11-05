from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.role import Role
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter(prefix="/roles", tags=["Roles"])

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return current_user

def serialize_role(r: Role) -> dict:
    return {"id": r.id, "name": r.name}

@router.get("", response_model=List[dict])
def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    roles = db.query(Role).order_by(Role.id.asc()).all()
    return [serialize_role(r) for r in roles]

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_role(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    name = (data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Role name required")
    if db.query(Role).filter(Role.name == name).first():
        raise HTTPException(status_code=400, detail="Role already exists")
    r = Role(name=name)
    db.add(r); db.commit(); db.refresh(r)
    return {"message": "Role created", "role": serialize_role(r)}

@router.delete("/{role_id}", response_model=dict)
def delete_role(
    role_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    r = db.query(Role).filter(Role.id == role_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    if r.name in ("admin", "standard_user"):
        raise HTTPException(status_code=400, detail="Cannot delete built-in role")
    db.delete(r); db.commit()
    return {"message": "Role deleted", "deleted_role_id": role_id}

@router.post("/assign", response_model=dict)
def assign_role(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    username = (data.get("username") or "").strip()
    role_name = (data.get("role") or "").strip()
    if not username or not role_name:
        raise HTTPException(status_code=400, detail="username and role required")
    u = db.query(User).filter(User.username == username).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    r = db.query(Role).filter(Role.name == role_name).first()
    if not r:
        raise HTTPException(status_code=404, detail="Role not found")
    u.role = r.name
    db.commit(); db.refresh(u)
    return {"message": "Role assigned", "user": {"id": u.id, "username": u.username, "role": u.role}}
