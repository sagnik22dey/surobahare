import os
import secrets
import httpx
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from storage import add_enrollment, get_all_enrollments

router = APIRouter()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


@router.post("/enroll")
async def submit_enrollment(
    parent_name: str = Form(...),
    child_name: str = Form(...),
    child_age: int = Form(...),
    mobile: str = Form(...),
    location: str = Form(...),
    program_interest: str = Form(...),
    heard_from: Optional[str] = Form(None),
):
    record = {
        "parent_name": parent_name,
        "child_name": child_name,
        "child_age": child_age,
        "mobile": mobile,
        "location": location,
        "program_interest": program_interest,
        "heard_from": heard_from or "",
    }
    add_enrollment(record)

    try:
        whatsapp_number = os.getenv("ADMIN_WHATSAPP_NUMBER", "")
        api_key = os.getenv("CALLMEBOT_API_KEY", "")
        if whatsapp_number and api_key:
            message = (
                f"🎵 New Enrollment!\n"
                f"Parent: {parent_name}\n"
                f"Child: {child_name} (Age: {child_age})\n"
                f"Mobile: {mobile}\n"
                f"Location: {location}\n"
                f"Program: {program_interest}"
            )
            url = (
                f"https://api.callmebot.com/whatsapp.php"
                f"?phone={whatsapp_number}&text={message}&apikey={api_key}"
            )
            async with httpx.AsyncClient() as client:
                await client.get(url, timeout=5)
    except Exception:
        pass

    return RedirectResponse(url="/thankyou", status_code=303)


@router.get("/admin/enrollments")
async def admin_enrollments(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
):
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    correct_user = secrets.compare_digest(credentials.username, admin_user)
    correct_pass = secrets.compare_digest(credentials.password, admin_password)

    if not (correct_user and correct_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    enrollments = get_all_enrollments()
    return templates.TemplateResponse(
        "admin_enrollments.html",
        {"request": request, "enrollments": enrollments},
    )
