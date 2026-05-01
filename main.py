import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from database import engine, SessionLocal
from models import Base, SiteContent
from routers import enrollment
from routers import admin_content
from storage import load_content

load_dotenv()


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_from_json()
    yield


app = FastAPI(title="Sur-O-Bahare Music Academy", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(enrollment.router)
app.include_router(admin_content.router)


def get_content():
    return load_content()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "content": get_content()})


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "content": get_content()})


@app.get("/programs")
async def programs(request: Request):
    return templates.TemplateResponse("programs.html", {"request": request, "content": get_content()})


@app.get("/gallery")
async def gallery(request: Request):
    return templates.TemplateResponse("gallery.html", {"request": request, "content": get_content()})


@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request, "content": get_content()})


@app.get("/thankyou")
async def thankyou(request: Request):
    return templates.TemplateResponse("thankyou.html", {"request": request, "content": get_content()})
