from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Request, Depends
from models import AdminUser
from routers.auth import get_current_admin
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
async def admin_dashboard(request: Request, current_admin: AdminUser = Depends(get_current_admin)):
    return templates.TemplateResponse(request, "admin.html", {})


# ─── Media Upload (images, audio, video, documents) ───────────────────────────

@router.post("/upload-media")
@router.post("/upload-image")
async def upload_media(file: UploadFile = File(...), current_admin: AdminUser = Depends(get_current_admin)):
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
async def get_content_api(current_admin: AdminUser = Depends(get_current_admin)):
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
async def update_hero(data: HeroUpdate, current_admin: AdminUser = Depends(get_current_admin)):
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
async def update_mentor(data: MentorUpdate, current_admin: AdminUser = Depends(get_current_admin)):
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
    visible: Optional[bool] = True
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
async def update_programs(data: ProgramsUpdate, current_admin: AdminUser = Depends(get_current_admin)):
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
                "visible": p.visible if p.visible is not None else True,
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
    visible: Optional[bool] = True
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
async def update_teaching_approach(data: TeachingApproachUpdate, current_admin: AdminUser = Depends(get_current_admin)):
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
                "visible": p.visible if p.visible is not None else True,
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
    visible: Optional[bool] = True
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
async def update_testimonials(data: TestimonialsUpdate, current_admin: AdminUser = Depends(get_current_admin)):
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
                "visible": item.visible if item.visible is not None else True,
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
async def update_admissions_banner(data: AdmissionsBannerUpdate, current_admin: AdminUser = Depends(get_current_admin)):
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
    visible: Optional[bool] = True
    icon: Optional[str] = "⭐"
    label_en: str
    label_bn: str


class MeteorHighlightsUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    items: Optional[List[HighlightItem]] = None


@router.put("/meteor-highlights")
async def update_meteor_highlights(data: MeteorHighlightsUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    mh = content.setdefault("meteor_highlights", {})
    if data.title_en is not None: mh.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: mh.setdefault("title", {})["bn"] = data.title_bn
    if data.items is not None:
        mh["items"] = [
            {
                "id": item.id or f"h{i + 1}",
                "visible": item.visible if item.visible is not None else True,
                "icon": item.icon or "⭐",
                "label_en": item.label_en,
                "label_bn": item.label_bn,
            }
            for i, item in enumerate(data.items)
        ]
    save_section("meteor_highlights", mh)
    return {"status": "ok", "section": "meteor_highlights"}


# ─── CONTACT INFO ─────────────────────────────────────────────────────────────

class ContactInfoUpdate(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    address_en: Optional[str] = None
    address_bn: Optional[str] = None
    whatsapp_number: Optional[str] = None

@router.put("/contact-info")
async def update_contact_info(data: ContactInfoUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    ci = content.setdefault("contact_info", {})
    if data.phone is not None: ci["phone"] = data.phone
    if data.email is not None: ci["email"] = data.email
    if data.address_en is not None: ci.setdefault("address", {})["en"] = data.address_en
    if data.address_bn is not None: ci.setdefault("address", {})["bn"] = data.address_bn
    if data.whatsapp_number is not None: ci["whatsapp_number"] = data.whatsapp_number
    save_section("contact_info", ci)
    return {"status": "ok", "section": "contact_info"}


# ─── FOOTER INFO ──────────────────────────────────────────────────────────────

class FooterInfoUpdate(BaseModel):
    tagline_en: Optional[str] = None
    tagline_bn: Optional[str] = None
    copyright_en: Optional[str] = None
    copyright_bn: Optional[str] = None

@router.put("/footer-info")
async def update_footer_info(data: FooterInfoUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    fi = content.setdefault("footer_info", {})
    if data.tagline_en is not None: fi.setdefault("tagline", {})["en"] = data.tagline_en
    if data.tagline_bn is not None: fi.setdefault("tagline", {})["bn"] = data.tagline_bn
    if data.copyright_en is not None: fi.setdefault("copyright", {})["en"] = data.copyright_en
    if data.copyright_bn is not None: fi.setdefault("copyright", {})["bn"] = data.copyright_bn
    save_section("footer_info", fi)
    return {"status": "ok", "section": "footer_info"}


# ─── ABOUT PAGE ───────────────────────────────────────────────────────────────

class AboutPageUpdate(BaseModel):
    hero_title_en: Optional[str] = None
    hero_title_bn: Optional[str] = None
    hero_subtitle_en: Optional[str] = None
    hero_subtitle_bn: Optional[str] = None
    story_title_en: Optional[str] = None
    story_title_bn: Optional[str] = None
    story_p1_en: Optional[str] = None
    story_p1_bn: Optional[str] = None
    story_p2_en: Optional[str] = None
    story_p2_bn: Optional[str] = None
    story_p3_en: Optional[str] = None
    story_p3_bn: Optional[str] = None

@router.put("/about-page")
async def update_about_page(data: AboutPageUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    ap = content.setdefault("about_page", {})
    if data.hero_title_en is not None: ap.setdefault("hero_title", {})["en"] = data.hero_title_en
    if data.hero_title_bn is not None: ap.setdefault("hero_title", {})["bn"] = data.hero_title_bn
    if data.hero_subtitle_en is not None: ap.setdefault("hero_subtitle", {})["en"] = data.hero_subtitle_en
    if data.hero_subtitle_bn is not None: ap.setdefault("hero_subtitle", {})["bn"] = data.hero_subtitle_bn
    if data.story_title_en is not None: ap.setdefault("story_title", {})["en"] = data.story_title_en
    if data.story_title_bn is not None: ap.setdefault("story_title", {})["bn"] = data.story_title_bn
    if data.story_p1_en is not None: ap.setdefault("story_p1", {})["en"] = data.story_p1_en
    if data.story_p1_bn is not None: ap.setdefault("story_p1", {})["bn"] = data.story_p1_bn
    if data.story_p2_en is not None: ap.setdefault("story_p2", {})["en"] = data.story_p2_en
    if data.story_p2_bn is not None: ap.setdefault("story_p2", {})["bn"] = data.story_p2_bn
    if data.story_p3_en is not None: ap.setdefault("story_p3", {})["en"] = data.story_p3_en
    if data.story_p3_bn is not None: ap.setdefault("story_p3", {})["bn"] = data.story_p3_bn
    save_section("about_page", ap)
    return {"status": "ok", "section": "about_page"}


# ─── GALLERY PAGE ─────────────────────────────────────────────────────────────

class GalleryItem(BaseModel):
    id: Optional[str] = None
    visible: Optional[bool] = True
    image_url: str

class GalleryPageUpdate(BaseModel):
    hero_title_en: Optional[str] = None
    hero_title_bn: Optional[str] = None
    hero_subtitle_en: Optional[str] = None
    hero_subtitle_bn: Optional[str] = None
    story_title_en: Optional[str] = None
    story_title_bn: Optional[str] = None
    story_desc_en: Optional[str] = None
    story_desc_bn: Optional[str] = None
    images: Optional[List[GalleryItem]] = None

@router.put("/gallery-page")
async def update_gallery_page(data: GalleryPageUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    gp = content.setdefault("gallery_page", {})
    if data.hero_title_en is not None: gp.setdefault("hero_title", {})["en"] = data.hero_title_en
    if data.hero_title_bn is not None: gp.setdefault("hero_title", {})["bn"] = data.hero_title_bn
    if data.hero_subtitle_en is not None: gp.setdefault("hero_subtitle", {})["en"] = data.hero_subtitle_en
    if data.hero_subtitle_bn is not None: gp.setdefault("hero_subtitle", {})["bn"] = data.hero_subtitle_bn
    if data.story_title_en is not None: gp.setdefault("story_title", {})["en"] = data.story_title_en
    if data.story_title_bn is not None: gp.setdefault("story_title", {})["bn"] = data.story_title_bn
    if data.story_desc_en is not None: gp.setdefault("story_desc", {})["en"] = data.story_desc_en
    if data.story_desc_bn is not None: gp.setdefault("story_desc", {})["bn"] = data.story_desc_bn
    if data.images is not None:
        gp["images"] = [
            {
                "id": item.id or f"img{i+1}", 
                "visible": item.visible if item.visible is not None else True,
                "image_url": item.image_url
            }
            for i, item in enumerate(data.images)
        ]
    save_section("gallery_page", gp)
    return {"status": "ok", "section": "gallery_page"}


# ─── CONTACT PAGE ─────────────────────────────────────────────────────────────

class ContactPageUpdate(BaseModel):
    hero_title_en: Optional[str] = None
    hero_title_bn: Optional[str] = None
    hero_subtitle_en: Optional[str] = None
    hero_subtitle_bn: Optional[str] = None

@router.put("/contact-page")
async def update_contact_page(data: ContactPageUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    cp = content.setdefault("contact_page", {})
    if data.hero_title_en is not None: cp.setdefault("hero_title", {})["en"] = data.hero_title_en
    if data.hero_title_bn is not None: cp.setdefault("hero_title", {})["bn"] = data.hero_title_bn
    if data.hero_subtitle_en is not None: cp.setdefault("hero_subtitle", {})["en"] = data.hero_subtitle_en
    if data.hero_subtitle_bn is not None: cp.setdefault("hero_subtitle", {})["bn"] = data.hero_subtitle_bn
    save_section("contact_page", cp)
    return {"status": "ok", "section": "contact_page"}


# ─── THANKYOU PAGE ────────────────────────────────────────────────────────────

class ThankyouPageUpdate(BaseModel):
    title_en: Optional[str] = None
    title_bn: Optional[str] = None
    message_en: Optional[str] = None
    message_bn: Optional[str] = None

@router.put("/thankyou-page")
async def update_thankyou_page(data: ThankyouPageUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    tp = content.setdefault("thankyou_page", {})
    if data.title_en is not None: tp.setdefault("title", {})["en"] = data.title_en
    if data.title_bn is not None: tp.setdefault("title", {})["bn"] = data.title_bn
    if data.message_en is not None: tp.setdefault("message", {})["en"] = data.message_en
    if data.message_bn is not None: tp.setdefault("message", {})["bn"] = data.message_bn
    save_section("thankyou_page", tp)
    return {"status": "ok", "section": "thankyou_page"}


# ─── MUSIC SETTINGS ───────────────────────────────────────────────────────────

class MusicSettingsUpdate(BaseModel):
    global_default_url: Optional[str] = None
    home_music_url: Optional[str] = None
    about_music_url: Optional[str] = None
    programs_music_url: Optional[str] = None
    gallery_music_url: Optional[str] = None
    contact_music_url: Optional[str] = None
    thankyou_music_url: Optional[str] = None

@router.put("/music-settings")
async def update_music_settings(data: MusicSettingsUpdate, current_admin: AdminUser = Depends(get_current_admin)):
    content = load_content()
    ms = content.setdefault("music_settings", {})
    if data.global_default_url is not None: ms["global_default_url"] = data.global_default_url
    if data.home_music_url is not None: ms["home_music_url"] = data.home_music_url
    if data.about_music_url is not None: ms["about_music_url"] = data.about_music_url
    if data.programs_music_url is not None: ms["programs_music_url"] = data.programs_music_url
    if data.gallery_music_url is not None: ms["gallery_music_url"] = data.gallery_music_url
    if data.contact_music_url is not None: ms["contact_music_url"] = data.contact_music_url
    if data.thankyou_music_url is not None: ms["thankyou_music_url"] = data.thankyou_music_url
    save_section("music_settings", ms)
    return {"status": "ok", "section": "music_settings"}
