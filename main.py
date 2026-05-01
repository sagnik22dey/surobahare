from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from routers import enrollment
from routers import admin_content
from storage import load_content

load_dotenv()

app = FastAPI(title="Sur-O-Bahare Music Academy")

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
