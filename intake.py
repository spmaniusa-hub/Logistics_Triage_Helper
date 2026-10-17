from __future__ import annotations
from dataclasses import dataclass

ALLOWED_CATEGORIES = {"delay", "damaged", "missing", "billing", "other"}
ALLOWED_PRIORITIES = {"P1", "P2", "P3", "P4"}

@dataclass
class Complaint:
    complaint_id: str
    text: str
    category: str | None = None
    priority: str | None = None


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def can_auto_route(record: dict) -> bool:
    required = {"category", "priority", "summary", "needs_human"}
    if set(record) != required:
        return False
    if record["category"] not in ALLOWED_CATEGORIES:
        return False
    if record["priority"] not in ALLOWED_PRIORITIES:
        return False
    if record["needs_human"] is not False:
        return False
    return bool(record["summary"])


def build_record(complaint: Complaint, triage: dict) -> dict:
    return {
        "complaint_id": complaint.complaint_id,
        "original_text": normalize_text(complaint.text),
        "category": triage.get("category", "other"),
        "priority": triage.get("priority", "P4"),
        "summary": triage.get("summary", ""),
        "needs_human": triage.get("needs_human", True),
        "auto_route": can_auto_route(triage),
    }
