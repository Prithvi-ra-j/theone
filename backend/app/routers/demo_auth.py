"""Demo authentication routes for development/prototype only."""
import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.utils.jwt import create_access_token

router = APIRouter()


class DemoLoginIn(BaseModel):
    email: str = "demo@example.com"


@router.post("/auth/demo-login")
def demo_login(payload: DemoLoginIn, db: Session = Depends(get_db)):
    """Return a long-lived token for a demo email. Creates user if missing.

    This route is intended for development only. It is enabled when the
    environment variable ENABLE_DEMO_LOGIN is not set to "0" or "false".
    """
    if os.environ.get("ENABLE_DEMO_LOGIN", "1").lower() in ("0", "false"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo login disabled")

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(email=payload.email, name="Demo User")
        db.add(user)
        db.commit()
        db.refresh(user)

    # create token; signature of helper may differ so we try a couple of forms
    try:
        token = create_access_token(subject=str(user.id), expires_delta=timedelta(days=30))
    except TypeError:
        token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(days=30))

    return {"access_token": token, "token_type": "bearer"}
