from typing import Any, Dict, List
from sqlalchemy.orm import Session
from models import SiteContent, Enrollment
from database import SessionLocal


def _get_db() -> Session:
    return SessionLocal()


def load_content() -> Dict[str, Any]:
    db = _get_db()
    try:
        rows = db.query(SiteContent).all()
        return {row.key: row.value for row in rows}
    finally:
        db.close()


def save_content(data: Dict[str, Any]) -> None:
    db = _get_db()
    try:
        for key, value in data.items():
            existing = db.query(SiteContent).filter(SiteContent.key == key).first()
            if existing:
                existing.value = value
            else:
                db.add(SiteContent(key=key, value=value))
        db.commit()
    finally:
        db.close()


def extract_urls(data: Any, endpoint: str) -> set:
    urls = set()
    if isinstance(data, dict):
        for v in data.values():
            urls.update(extract_urls(v, endpoint))
    elif isinstance(data, list):
        for item in data:
            urls.update(extract_urls(item, endpoint))
    elif isinstance(data, str) and data.startswith(endpoint):
        urls.add(data)
    return urls

def save_section(key: str, value: Any) -> None:
    """Upsert a single content section by key."""
    db = _get_db()
    try:
        existing = db.query(SiteContent).filter(SiteContent.key == key).first()
        if existing:
            try:
                from bucket import _ENDPOINT, delete_file
                old_urls = extract_urls(existing.value, _ENDPOINT)
                new_urls = extract_urls(value, _ENDPOINT)
                orphaned = old_urls - new_urls
                for url in orphaned:
                    delete_file(url)
            except Exception as e:
                print(f"Failed to cleanup orphaned files: {e}")
                
            existing.value = value
        else:
            db.add(SiteContent(key=key, value=value))
        db.commit()
    finally:
        db.close()


def add_enrollment(record: Dict[str, Any]) -> None:
    db = _get_db()
    try:
        enrollment = Enrollment(
            parent_name=record["parent_name"],
            child_name=record["child_name"],
            child_age=int(record["child_age"]),
            mobile=record["mobile"],
            location=record["location"],
            program_interest=record["program_interest"],
            heard_from=record.get("heard_from") or None,
        )
        db.add(enrollment)
        db.commit()
    finally:
        db.close()


def get_all_enrollments() -> List[Dict[str, Any]]:
    db = _get_db()
    try:
        rows = db.query(Enrollment).order_by(Enrollment.created_at.desc()).all()
        return [
            {
                "id": r.id,
                "parent_name": r.parent_name,
                "child_name": r.child_name,
                "child_age": r.child_age,
                "mobile": r.mobile,
                "location": r.location,
                "program_interest": r.program_interest,
                "heard_from": r.heard_from or "",
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in rows
        ]
    finally:
        db.close()
