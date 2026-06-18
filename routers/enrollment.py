import os
from typing import Optional
from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from storage import add_enrollment, get_all_enrollments
from routers.auth import get_current_admin
from models import AdminUser
from whatsapp_queue import enqueue_whatsapp_message

router = APIRouter()
templates = Jinja2Templates(directory="templates")


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
        admin_number = os.getenv("ADMIN_WHATSAPP_NUMBER", "")
        if admin_number:
            message = (
                f"🎓 *New Enrollment — Sur-O-Bahare*\n\n"
                f"👤 Parent: {parent_name}\n"
                f"👶 Child: {child_name} (Age: {child_age})\n"
                f"📱 Mobile: {mobile}\n"
                f"📍 Location: {location}\n"
                f"🎶 Program: {program_interest}"
            )
            if heard_from:
                message += f"\n📣 Heard from: {heard_from}"
            enqueue_whatsapp_message(admin_number, message)
    except Exception:
        pass

    return RedirectResponse(url="/thankyou", status_code=303)


@router.get("/admin/enrollments")
async def admin_enrollments(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
):
    enrollments = get_all_enrollments()
    return templates.TemplateResponse(
        request,
        "admin_enrollments.html",
        {"enrollments": enrollments},
    )
