from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from storage import load_content, save_section
from bucket import upload_file, validate_and_detect

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


# ─── Admin Dashboard Page ─────────────────────────────────────────────────────

@router.get("")
@router.get("/")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(request, "admin.html", {})


# ─── Media Upload (images, audio, video, documents) ───────────────────────────

@router.post("/upload-media")
async def upload_media(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 50 MB.")
    try:
        url = upload_file(content, file.filename or "upload", file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"url": url}


# ─── Full Content Get ─────────────────────────────────────────────────────────

@router.get("/content")
async def get_content():
    return load_content()


# ─── HERO ─────────────────────────────────────────────────────────────────────

class HeroUpdate(BaseModel):
    badge_en: Optional[str] = None
    badge_bn: Optional[str] = None
    headline_en: Optional[str] = None
    headline_bn: Optional[str] = None
    tagline_en: Optional[str] = None
    tagline_bn: Optional[str] = None
    description_en: Optional[str] = None
    description_bn: Optional[str] = None
    bg_image_url: Optional[str] = None
    cta_primary_label_en: Optional[str] = None
    cta_primary_label_bn: Optional[str] = None
    cta_primary_link: Optional[str] = None
    cta_secondary_label_en: Optional[str] = None
    cta_secondary_label_bn: Optional[str] = None
    cta_secondary_link: Optional[str] = None


@router.put("/hero")
async def update_hero(data: HeroUpdate):
    content = load_content()
    h = content.setdefault("hero", {})
    if data.badge_en is not None: h.setdefault("badge", {})["en"] = data.badge_en
    if data.badge_bn is not None: h.setdefault("badge", {})["bn"] = data.badge_bn
    if data.headline_en is not None: h.setdefault("headline", {})["en"] = data.headline_en
    if data.headline_bn is not None: h.setdefault("headline", {})["bn"] = data.headline_bn
    if data.tagline_en is not None: h.setdefault("tagline", {})["en"] = data.tagline_en
    if data.tagline_bn is not None: h.setdefault("tagline", {})["bn"] = data.tagline_bn
    if data.description_en is not None: h.setdefault("description", {})["en"] = data.description_en
    if data.description_bn is not None: h.setdefault("description", {})["bn"] = data.description_bn
    if data.bg_image_url is not None: h["bg_image_url"] = data.bg_image_url
    if data.cta_primary_label_en is not None: h["cta_primary_label_en"] = data.cta_primary_label_en
    if data.cta_primary_label_bn is not None: h["cta_primary_label_bn"] = data.cta_primary_label_bn
    if data.cta_primary_link is not None: h["cta_primary_link"] = data.cta_primary_link
    if data.cta_secondary_label_en is not None: h["cta_secondary_label_en"] = data.cta_secondary_label_en
    if data.cta_secondary_label_bn is not None: h["cta_secondary_label_bn"] = data.cta_secondary_label_bn
    if data.cta_secondary_link is not None: h["cta_secondary_link"] = data.cta_secondary_link
    save_section("hero", h)
    return {"status": "ok", "section": "hero"}


# ─── MENTOR ───────────────────────────────────────────────────────────────────

class MentorUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    name_en: Optional[str] = None
    name_bn: Optional[str] = None
    role_en: Optional[str] = None
    role_bn: Optional[str] = None
    bio_en: Optional[str] = None
    bio_bn: Optional[str] = None
    photo_url: Optional[str] = None
    qualifications: Optional[str] = None
    link: Optional[str] = None


@router.put("/mentor")
async def update_mentor(data: MentorUpdate):
    content = load_content()
    m = content.setdefault("about_snapshot", {})
    if data.title_en is not None: m.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: m.setdefault("title", {})["bn"] = data.title_bn
    if data.name_en is not None: m.setdefault("mentor_name", {})["en"] = data.name_en
    if data.name_bn is not None: m.setdefault("mentor_name", {})["bn"] = data.name_bn
    if data.role_en is not None: m.setdefault("mentor_role", {})["en"] = data.role_en
    if data.role_bn is not None: m.setdefault("mentor_role", {})["bn"] = data.role_bn
    if data.bio_en is not None: m.setdefault("mentor_bio", {})["en"] = data.bio_en
    if data.bio_bn is not None: m.setdefault("mentor_bio", {})["bn"] = data.bio_bn
    if data.photo_url is not None: m["mentor_photo_url"] = data.photo_url
    if data.qualifications is not None: m["mentor_qualifications"] = data.qualifications
    if data.link is not None: m["mentor_link"] = data.link
    save_section("about_snapshot", m)
    return {"status": "ok", "section": "about_snapshot"}


# ─── PROGRAMS ────────────────────────────────────────────────────────────────

class ProgramItem(BaseModel):
    id: Optional[str] = None
    title_en: str
    title_bn: str
    desc_en: str
    desc_bn: str
    image_url: Optional[str] = ""
    icon: Optional[str] = "🎵"


class ProgramsUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    programs: Optional[List[ProgramItem]] = None


@router.put("/programs")
async def update_programs(data: ProgramsUpdate):
    content = load_content()
    pt = content.setdefault("programs_teaser", {})
    if data.title_en is not None: pt.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: pt.setdefault("title", {})["bn"] = data.title_bn
    if data.subtitle_en is not None: pt.setdefault("subtitle", {})["en"] = data.subtitle_en
    if data.subtitle_bn is not None: pt.setdefault("subtitle", {})["bn"] = data.subtitle_bn
    if data.programs is not None:
        pt["programs"] = [
            {
                "id": p.id or f"p{i + 1}",
                "title_en": p.title_en,
                "title_bn": p.title_bn,
                "desc_en": p.desc_en,
                "desc_bn": p.desc_bn,
                "image_url": p.image_url or "",
                "icon": p.icon or "🎵",
            }
            for i, p in enumerate(data.programs)
        ]
    save_section("programs_teaser", pt)
    return {"status": "ok", "section": "programs_teaser"}


# ─── TEACHING APPROACH ────────────────────────────────────────────────────────

class ApproachPoint(BaseModel):
    id: Optional[str] = None
    icon: Optional[str] = "ri-checkbox-circle-fill"
    en: str
    bn: str


class TeachingApproachUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    points: Optional[List[ApproachPoint]] = None


@router.put("/teaching-approach")
async def update_teaching_approach(data: TeachingApproachUpdate):
    content = load_content()
    ta = content.setdefault("teaching_approach", {})
    if data.title_en is not None: ta.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: ta.setdefault("title", {})["bn"] = data.title_bn
    if data.subtitle_en is not None: ta.setdefault("subtitle", {})["en"] = data.subtitle_en
    if data.subtitle_bn is not None: ta.setdefault("subtitle", {})["bn"] = data.subtitle_bn
    if data.points is not None:
        ta["points"] = [
            {
                "id": p.id or f"t{i + 1}",
                "icon": p.icon or "ri-checkbox-circle-fill",
                "en": p.en,
                "bn": p.bn,
            }
            for i, p in enumerate(data.points)
        ]
    save_section("teaching_approach", ta)
    return {"status": "ok", "section": "teaching_approach"}


# ─── TESTIMONIALS ─────────────────────────────────────────────────────────────

class TestimonialItem(BaseModel):
    id: Optional[str] = None
    quote_en: str
    quote_bn: str
    author_en: str
    author_bn: str
    rating: Optional[int] = 5
    photo_url: Optional[str] = ""


class TestimonialsUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    subtitle_en: Optional[str] = None
    subtitle_bn: Optional[str] = None
    list: Optional[List[TestimonialItem]] = None


@router.put("/testimonials")
async def update_testimonials(data: TestimonialsUpdate):
    content = load_content()
    t = content.setdefault("testimonials", {})
    if data.title_en is not None: t.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: t.setdefault("title", {})["bn"] = data.title_bn
    if data.subtitle_en is not None: t.setdefault("subtitle", {})["en"] = data.subtitle_en
    if data.subtitle_bn is not None: t.setdefault("subtitle", {})["bn"] = data.subtitle_bn
    if data.list is not None:
        t["list"] = [
            {
                "id": item.id or f"test{i + 1}",
                "quote_en": item.quote_en,
                "quote_bn": item.quote_bn,
                "author_en": item.author_en,
                "author_bn": item.author_bn,
                "rating": item.rating or 5,
                "photo_url": item.photo_url or "",
            }
            for i, item in enumerate(data.list)
        ]
    save_section("testimonials", t)
    return {"status": "ok", "section": "testimonials"}


# ─── ADMISSIONS BANNER ────────────────────────────────────────────────────────

class AdmissionsBannerUpdate(BaseModel):
    visible: Optional[bool] = None
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    description_en: Optional[str] = None
    description_bn: Optional[str] = None
    urgency_text_en: Optional[str] = None
    urgency_text_bn: Optional[str] = None
    seat_count: Optional[str] = None
    enroll_btn_label_en: Optional[str] = None
    enroll_btn_label_bn: Optional[str] = None
    enroll_btn_link: Optional[str] = None
    whatsapp_number: Optional[str] = None
    whatsapp_message: Optional[str] = None
    whatsapp_btn_label_en: Optional[str] = None
    whatsapp_btn_label_bn: Optional[str] = None


@router.put("/admissions-banner")
async def update_admissions_banner(data: AdmissionsBannerUpdate):
    content = load_content()
    ab = content.setdefault("admissions_banner", {})
    if data.visible is not None: ab["visible"] = data.visible
    if data.title_en is not None: ab.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: ab.setdefault("title", {})["bn"] = data.title_bn
    if data.description_en is not None: ab.setdefault("description", {})["en"] = data.description_en
    if data.description_bn is not None: ab.setdefault("description", {})["bn"] = data.description_bn
    if data.urgency_text_en is not None: ab["urgency_text_en"] = data.urgency_text_en
    if data.urgency_text_bn is not None: ab["urgency_text_bn"] = data.urgency_text_bn
    if data.seat_count is not None: ab["seat_count"] = data.seat_count
    if data.enroll_btn_label_en is not None: ab["enroll_btn_label_en"] = data.enroll_btn_label_en
    if data.enroll_btn_label_bn is not None: ab["enroll_btn_label_bn"] = data.enroll_btn_label_bn
    if data.enroll_btn_link is not None: ab["enroll_btn_link"] = data.enroll_btn_link
    if data.whatsapp_number is not None: ab["whatsapp_number"] = data.whatsapp_number
    if data.whatsapp_message is not None: ab["whatsapp_message"] = data.whatsapp_message
    if data.whatsapp_btn_label_en is not None: ab["whatsapp_btn_label_en"] = data.whatsapp_btn_label_en
    if data.whatsapp_btn_label_bn is not None: ab["whatsapp_btn_label_bn"] = data.whatsapp_btn_label_bn
    save_section("admissions_banner", ab)
    return {"status": "ok", "section": "admissions_banner"}


# ─── METEOR HIGHLIGHTS ────────────────────────────────────────────────────────

class HighlightItem(BaseModel):
    id: Optional[str] = None
    icon: Optional[str] = "⭐"
    label_en: str
    label_bn: str


class MeteorHighlightsUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    items: Optional[List[HighlightItem]] = None


@router.put("/meteor-highlights")
async def update_meteor_highlights(data: MeteorHighlightsUpdate):
    content = load_content()
    mh = content.setdefault("meteor_highlights", {})
    if data.title_en is not None: mh.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: mh.setdefault("title", {})["bn"] = data.title_bn
    if data.items is not None:
        mh["items"] = [
            {
                "id": item.id or f"h{i + 1}",
                "icon": item.icon or "⭐",
                "label_en": item.label_en,
                "label_bn": item.label_bn,
            }
            for i, item in enumerate(data.items)
        ]
    save_section("meteor_highlights", mh)
    return {"status": "ok", "section": "meteor_highlights"}
