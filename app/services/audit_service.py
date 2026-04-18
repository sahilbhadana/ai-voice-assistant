import json

from app.db.models import AuditLog


def write_audit_log(db, actor, action: str, resource_type: str, resource_id=None, details: dict = None):
    log = AuditLog(
        actor_user_id=getattr(actor, "id", None),
        actor_email=getattr(actor, "email", None) if actor else None,
        actor_role=getattr(actor, "role", None) if actor else None,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        details=json.dumps(details or {}, sort_keys=True),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_logs(db, limit: int = 100):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "actor_email": log.actor_email,
            "actor_role": log.actor_role,
            "action": log.action,
            "resource_type": log.resource_type,
            "resource_id": log.resource_id,
            "details": json.loads(log.details or "{}"),
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
