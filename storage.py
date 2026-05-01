import json
import os
from datetime import datetime
from typing import List, Dict, Any

ENROLLMENTS_FILE = "enrollments.json"
CONTENT_FILE = "content.json"

def load_content() -> Dict[str, Any]:
    if not os.path.exists(CONTENT_FILE):
        return {}
    with open(CONTENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_content(data: Dict[str, Any]) -> None:
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load() -> List[Dict[str, Any]]:
    if not os.path.exists(ENROLLMENTS_FILE):
        return []
    with open(ENROLLMENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: List[Dict[str, Any]]) -> None:
    with open(ENROLLMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def add_enrollment(record: Dict[str, Any]) -> Dict[str, Any]:
    data = _load()
    record["id"] = len(data) + 1
    record["created_at"] = datetime.now().isoformat()
    data.append(record)
    _save(data)
    return record


def get_all_enrollments() -> List[Dict[str, Any]]:
    data = _load()
    return list(reversed(data))
