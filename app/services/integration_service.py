import json
import os
from datetime import datetime, timedelta
from urllib import request

from app.db.models import Appointment, IntegrationSyncLog

SUPPORTED_TARGETS = ("ehr", "calendar")
RETRY_DELAY_MINUTES = 15


def _appointment_payload(appointment):
    return {
        "appointment_id": f"APT-{appointment.id}",
        "patient_name": appointment.patient_name,
        "patient_email": appointment.patient_email,
        "doctor_id": appointment.doctor_id,
        "doctor_name": appointment.doctor_name,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time,
        "status": appointment.status,
    }


def _post_webhook(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        body = response.read().decode("utf-8")
        return response.status, body


def _target_webhooks():
    return {
        "ehr": os.getenv("EHR_WEBHOOK_URL"),
        "calendar": os.getenv("CALENDAR_WEBHOOK_URL"),
    }


def _target_list(target_system: str):
    targets = list(SUPPORTED_TARGETS) if target_system == "all" else [target_system]
    invalid_targets = [target for target in targets if target not in SUPPORTED_TARGETS]
    if invalid_targets:
        return None, f"Unsupported integration target: {', '.join(invalid_targets)}"
    return targets, None


def _extract_external_reference(body: str, status_code: int):
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        data = {}

    if isinstance(data, dict):
        for key in ("external_reference", "external_id", "id"):
            if data.get(key):
                return str(data[key])
    return str(status_code)


def _serialize_log(log):
    return {
        "sync_id": log.id,
        "target_system": log.target_system,
        "status": log.status,
        "external_reference": log.external_reference,
        "message": log.message,
        "synced_at": log.synced_at.isoformat(),
    }


def _sync_target(db, appointment, target: str, log: IntegrationSyncLog = None):
    webhook_url = _target_webhooks().get(target)
    payload = _appointment_payload(appointment)
    payload_json = json.dumps(payload, sort_keys=True)
    next_retry_at = datetime.utcnow() + timedelta(minutes=RETRY_DELAY_MINUTES)

    if log is None:
        log = IntegrationSyncLog(
            appointment_id=appointment.id,
            target_system=target,
        )
        db.add(log)
    else:
        log.attempts = (log.attempts or 0) + 1

    log.payload = payload_json
    log.synced_at = datetime.utcnow()

    if not webhook_url:
        log.status = "queued"
        log.external_reference = None
        log.message = f"{target.upper()} webhook is not configured"
        log.next_retry_at = next_retry_at
        db.commit()
        db.refresh(log)
        return log

    try:
        status_code, body = _post_webhook(webhook_url, payload)
        if not 200 <= status_code < 300:
            raise RuntimeError(f"{target.upper()} webhook returned HTTP {status_code}: {body[:500]}")

        external_reference = _extract_external_reference(body, status_code)
        if target == "ehr":
            appointment.external_ehr_id = external_reference
        if target == "calendar":
            appointment.external_calendar_id = external_reference

        log.status = "synced"
        log.external_reference = external_reference
        log.message = body[:500]
        log.next_retry_at = None
    except Exception as e:
        log.status = "failed"
        log.external_reference = None
        log.message = str(e)[:500]
        log.next_retry_at = next_retry_at

    db.commit()
    db.refresh(log)
    return log


def sync_appointment(db, appointment_id: int, target_system: str = "all"):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return {"error": "Appointment not found"}

    targets, error = _target_list(target_system)
    if error:
        return {"error": error}

    results = []
    for target in targets:
        log = _sync_target(db, appointment, target)
        results.append(_serialize_log(log))

    return {
        "appointment_id": f"APT-{appointment.id}",
        "sync_results": results,
    }


def retry_pending_syncs(db, limit: int = 20):
    now = datetime.utcnow()
    logs = (
        db.query(IntegrationSyncLog)
        .filter(
            IntegrationSyncLog.status.in_(["queued", "failed"]),
            IntegrationSyncLog.next_retry_at <= now,
        )
        .order_by(IntegrationSyncLog.next_retry_at.asc())
        .limit(limit)
        .all()
    )

    results = []
    for log in logs:
        appointment = db.query(Appointment).filter(Appointment.id == log.appointment_id).first()
        if not appointment:
            log.status = "failed"
            log.message = "Appointment not found"
            log.next_retry_at = None
            log.synced_at = datetime.utcnow()
            log.attempts = (log.attempts or 0) + 1
            db.commit()
            db.refresh(log)
            results.append({"error": "Appointment not found", "sync_id": log.id})
            continue

        updated_log = _sync_target(db, appointment, log.target_system, log=log)
        results.append(
            {
                "appointment_id": f"APT-{appointment.id}",
                "sync_results": [_serialize_log(updated_log)],
            }
        )
    return results


def get_sync_history(db, appointment_id: int):
    logs = (
        db.query(IntegrationSyncLog)
        .filter(IntegrationSyncLog.appointment_id == appointment_id)
        .order_by(IntegrationSyncLog.synced_at.desc())
        .all()
    )

    return {
        "appointment_id": f"APT-{appointment_id}",
        "sync_history": [
            {
                "sync_id": log.id,
                "target_system": log.target_system,
                "status": log.status,
                "external_reference": log.external_reference,
                "message": log.message,
                "synced_at": log.synced_at.isoformat(),
            }
            for log in logs
        ],
    }
