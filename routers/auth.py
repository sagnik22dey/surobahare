import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from sqlalchemy.orm import Session

from database import get_db
from models import AdminUser, AdminSession

router = APIRouter(prefix="/admin", tags=["auth"])
templates = Jinja2Templates(directory="templates")


SESSION_COOKIE_NAME = "admin_session"
SESSION_EXPIRY_DAYS = 7


def create_session(db: Session, user_id: int) -> str:
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)
    db_session = AdminSession(
        session_token=session_token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_session)
    db.commit()
    return session_token


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )

    db_session = db.query(AdminSession).filter(AdminSession.session_token == token).first()
    if not db_session or db_session.expires_at < datetime.utcnow():
        if db_session:
            db.delete(db_session)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )

    user = db.query(AdminUser).filter(AdminUser.id == db_session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )

    return user


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        # Check if valid
        return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request, "admin_login.html", {"error": None})


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return templates.TemplateResponse(
            request, 
            "admin_login.html", 
            {"error": "Invalid username or password"}
        )

    # Create session
    token = create_session(db, user.id)
    
    # Redirect to admin dashboard
    redirect = RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    redirect.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=SESSION_EXPIRY_DAYS * 24 * 60 * 60,
        samesite="lax",
    )
    return redirect


@router.get("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        db_session = db.query(AdminSession).filter(AdminSession.session_token == token).first()
        if db_session:
            db.delete(db_session)
            db.commit()
            
    redirect = RedirectResponse(url="/admin/login", status_code=status.HTTP_302_FOUND)
    redirect.delete_cookie(SESSION_COOKIE_NAME)
    return redirect


@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, "admin_forgot.html", {"error": None, "success": None})


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    username: str = Form(...),
    method: str = Form(...), # "old_password" or "recovery_code"
    old_password: Optional[str] = Form(None),
    recovery_code: Optional[str] = Form(None),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not user:
        return templates.TemplateResponse(
            request, 
            "admin_forgot.html", 
            {"error": "User not found", "success": None}
        )

    if method == "old_password":
        if not old_password or not bcrypt.checkpw(old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return templates.TemplateResponse(
                request, 
                "admin_forgot.html", 
                {"error": "Incorrect old password", "success": None}
            )
    elif method == "recovery_code":
        if not recovery_code or recovery_code != user.recovery_code:
            return templates.TemplateResponse(
                request, 
                "admin_forgot.html", 
                {"error": "Incorrect recovery code", "success": None}
            )
    else:
        return templates.TemplateResponse(
            request, 
            "admin_forgot.html", 
            {"error": "Invalid reset method", "success": None}
        )

    # Update password
    user.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.commit()

    return templates.TemplateResponse(
        request, 
        "admin_forgot.html", 
        {"error": None, "success": "Password changed successfully! You can now login."}
    )
