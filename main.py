import asyncio
import json
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from database import engine, SessionLocal
from models import Base, SiteContent
from routers import enrollment
from routers import admin_content
from routers import auth
from storage import load_content
from whatsapp_queue import process_queue

load_dotenv()

logger = logging.getLogger("whatsapp_queue")


def _seed_from_json():
    """Seed site_content from content.json if the table is empty."""
    json_path = os.path.join(os.path.dirname(__file__), "content.json")
    if not os.path.exists(json_path):
        return
    db = SessionLocal()
    try:
        existing = db.query(SiteContent).count()
        if existing > 0:
            return
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, value in data.items():
            db.add(SiteContent(key=key, value=value))
        db.commit()
        print(f"[startup] Seeded {len(data)} content sections from content.json")
    finally:
        db.close()

def _seed_admin_user():
    """Seed the default AdminUser if none exists."""
    from models import AdminUser
    import bcrypt
    db = SessionLocal()
    try:
        if db.query(AdminUser).count() == 0:
            username = os.getenv("ADMIN_USER", "surobahare")
            password = os.getenv("ADMIN_PASSWORD", "surobahare@123")
            recovery_code = os.getenv("ADMIN_RECOVERY_CODE", "RECOVERY123")
            
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            admin = AdminUser(
                username=username,
                password_hash=hashed,
                recovery_code=recovery_code
            )
            db.add(admin)
            db.commit()
            print(f"[startup] Seeded default AdminUser: {username}")
    finally:
        db.close()


async def _queue_worker():
    while True:
        try:
            await asyncio.get_event_loop().run_in_executor(None, process_queue)
        except Exception as e:
            logger.error(f"Queue worker error: {e}")
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_from_json()
    _seed_admin_user()
    task = asyncio.create_task(_queue_worker())
    yield
    task.cancel()


app = FastAPI(title="Sur-O-Bahare Music Academy", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(enrollment.router)
app.include_router(auth.router)
app.include_router(admin_content.router)


@app.get("/media/{key:path}")
async def media_proxy(key: str):
    from bucket import _get_client, _BUCKET
    client = _get_client()
    try:
        obj = client.get_object(Bucket=_BUCKET, Key=key)
        content_type = obj["ContentType"]
        body = obj["Body"]
        return StreamingResponse(body, media_type=content_type)
    except client.exceptions.NoSuchKey:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Media not found")
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Media not found")


def get_content():
    return load_content()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"content": get_content()})


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {"content": get_content()})


@app.get("/programs")
async def programs(request: Request):
    return templates.TemplateResponse(request, "programs.html", {"content": get_content()})


@app.get("/gallery")
async def gallery(request: Request):
    return templates.TemplateResponse(request, "gallery.html", {"content": get_content()})


@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html", {"content": get_content()})


@app.get("/thankyou")
async def thankyou(request: Request):
    return templates.TemplateResponse(request, "thankyou.html", {"content": get_content()})
