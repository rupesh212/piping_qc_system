from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from app.services.audit_service import log_action

router = APIRouter()


@router.get("/", response_model=list[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """List all users (admin only)."""
    users = (
        db.query(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return users


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Get a single user by ID (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a user's role and/or is_active flag (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    changed_fields: dict = {}
    if payload.role is not None and payload.role != user.role:
        changed_fields["role"] = {"from": user.role, "to": payload.role}
        user.role = payload.role
    if payload.is_active is not None and payload.is_active != user.is_active:
        changed_fields["is_active"] = {"from": user.is_active, "to": payload.is_active}
        user.is_active = payload.is_active

    if changed_fields:
        db.add(user)
        db.commit()
        db.refresh(user)
        log_action(
            db=db,
            action="USER_UPDATED",
            entity_type="user",
            user_id=current_user.id,
            entity_id=str(user_id),
            details=changed_fields,
        )

    return user


@router.delete("/{user_id}", response_model=UserOut)
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deactivate a user (set is_active=False). Admin only. Cannot deactivate self."""
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is already inactive")

    user.is_active = False
    db.add(user)
    db.commit()
    db.refresh(user)

    log_action(
        db=db,
        action="USER_DEACTIVATED",
        entity_type="user",
        user_id=current_user.id,
        entity_id=str(user_id),
        details={"username": user.username},
    )

    return user
