import json
import os
from urllib import request

from app.db.models import Appointment, IntegrationSyncLog

TARGET_WEBHOOKS = {
    "ehr": os.getenv("EHR_WEBHOOK_URL"),
    "calendar": os.getenv("CALENDAR_WEBHOOK_URL"),
}


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


def sync_appointment(db, appointment_id: int, target_system: str = "all"):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        return {"error": "Appointment not found"}

    targets = ["ehr", "calendar"] if target_system == "all" else [target_system]
    invalid_targets = [target for target in targets if target not in TARGET_WEBHOOKS]
    if invalid_targets:
        return {"error": f"Unsupported integration target: {', '.join(invalid_targets)}"}

    results = []

    for target in targets:
        webhook_url = TARGET_WEBHOOKS.get(target)
        payload = _appointment_payload(appointment)

        if not webhook_url:
            log = IntegrationSyncLog(
                appointment_id=appointment.id,
                target_system=target,
                status="queued",
                message=f"{target.upper()} webhook is not configured",
            )
        else:
            try:
                status_code, body = _post_webhook(webhook_url, payload)
                log = IntegrationSyncLog(
                    appointment_id=appointment.id,
                    target_system=target,
                    status="synced",
                    external_reference=str(status_code),
                    message=body[:500],
                )
            except Exception as e:
                log = IntegrationSyncLog(
                    appointment_id=appointment.id,
                    target_system=target,
                    status="failed",
                    message=str(e),
                )

        db.add(log)
        db.commit()
        db.refresh(log)
        results.append(
            {
                "sync_id": log.id,
                "target_system": log.target_system,
                "status": log.status,
                "external_reference": log.external_reference,
                "message": log.message,
                "synced_at": log.synced_at.isoformat(),
            }
        )

    return {
        "appointment_id": f"APT-{appointment.id}",
        "sync_results": results,
    }


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
