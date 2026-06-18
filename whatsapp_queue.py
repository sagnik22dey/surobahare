import os
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from models import WhatsAppMessage
from database import SessionLocal

logger = logging.getLogger("whatsapp_queue")

DAILY_LIMIT = 100

_ULTRAMSG_API = "https://api.ultramsg.com"


def _get_creds():
    return (
        os.getenv("ULTRAMSG_INSTANCE_ID", ""),
        os.getenv("ULTRAMSG_TOKEN", ""),
        os.getenv("ADMIN_WHATSAPP_NUMBER", ""),
    )


def _send_api(recipient: str, body: str) -> tuple[bool, str]:
    instance_id, token, _ = _get_creds()
    if not all([instance_id, token, recipient]):
        return False, "missing_config"

    import httpx

    url = f"{_ULTRAMSG_API}/{instance_id}/messages/chat"
    payload = f"token={token}&to={recipient}&body={body}"
    headers = {"content-type": "application/x-www-form-urlencoded"}

    try:
        resp = httpx.post(url, data=payload, headers=headers, timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("sent") == "true":
            return True, "ok"
        error = data.get("error", {})
        code = error.get("code", 0)
        if code == 211:
            return False, "rate_limited"
        if code in (212, 213, 214):
            return False, "invalid_number"
        return False, f"api_error_{code}"
    except Exception as e:
        return False, f"exception_{e}"


def enqueue_message(recipient: str, body: str):
    db = SessionLocal()
    try:
        msg = WhatsAppMessage(recipient=recipient, body=body, status="pending")
        db.add(msg)
        db.commit()
    finally:
        db.close()


def process_queue():
    db = SessionLocal()
    try:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(func.count(WhatsAppMessage.id)).filter(
            WhatsAppMessage.status == "sent",
            WhatsAppMessage.sent_at >= today_start,
        ).scalar()
        if today_count is None:
            today_count = 0

        if today_count >= DAILY_LIMIT:
            logger.info(f"Daily limit reached ({today_count}/{DAILY_LIMIT}). Retrying tomorrow.")
            return

        remaining = DAILY_LIMIT - today_count
        pending = (
            db.query(WhatsAppMessage)
            .filter(WhatsAppMessage.status == "pending")
            .order_by(WhatsAppMessage.created_at.asc())
            .limit(remaining)
            .all()
        )

        for msg in pending:
            ok, reason = _send_api(msg.recipient, msg.body)
            if ok:
                msg.status = "sent"
                msg.sent_at = datetime.utcnow()
            elif reason == "rate_limited":
                logger.warning("UltraMsg rate limit hit mid-batch. Stopping.")
                break
            elif reason in ("invalid_number", "missing_config"):
                msg.status = "failed"
            else:
                msg.retry_count += 1
                if msg.retry_count >= 5:
                    msg.status = "failed"
                    logger.warning(f"Message {msg.id} failed after 5 retries: {reason}")
                else:
                    logger.info(f"Message {msg.id} retry {msg.retry_count}: {reason}")

        db.commit()
        logger.info(f"Queue processed. Sent today: {today_count}, pending remaining: {db.query(WhatsAppMessage).filter(WhatsAppMessage.status == 'pending').count()}")
    finally:
        db.close()


def enqueue_whatsapp_message(recipient: str, body: str):
    db = SessionLocal()
    try:
        msg = WhatsAppMessage(recipient=recipient, body=body, status="pending")
        db.add(msg)
        db.commit()

        instance_id, token, _ = _get_creds()
        if not all([instance_id, token, recipient]):
            return

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = db.query(func.count(WhatsAppMessage.id)).filter(
            WhatsAppMessage.status == "sent",
            WhatsAppMessage.sent_at >= today_start,
        ).scalar() or 0

        if today_count >= DAILY_LIMIT:
            logger.info("Daily limit hit. Message queued for next batch.")
            return

        ok, reason = _send_api(msg.recipient, msg.body)
        if ok:
            msg.status = "sent"
            msg.sent_at = datetime.utcnow()
            db.commit()
        elif reason == "rate_limited":
            logger.warning("Rate limited on direct send. Message stays pending.")
            db.commit()
        else:
            msg.retry_count += 1
            db.commit()
    finally:
        db.close()
