from app.db.models import ConsentRecord, Patient


def capture_consent(
    db,
    patient_email: str,
    consent_type: str,
    granted: bool,
    captured_by: str = "system",
    source: str = "api",
    notes: str = None,
):
    patient = db.query(Patient).filter(Patient.email == patient_email).first()
    if not patient:
        return {"error": "Patient not found"}

    consent = ConsentRecord(
        patient_id=patient.id,
        consent_type=consent_type,
        granted=granted,
        captured_by=captured_by,
        source=source,
        notes=notes,
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)

    return {
        "message": "Consent captured",
        "consent_id": consent.id,
        "patient_email": patient.email,
        "consent_type": consent.consent_type,
        "granted": consent.granted,
        "captured_at": consent.captured_at.isoformat(),
    }


def latest_consent(db, patient_id: int, consent_type: str):
    return (
        db.query(ConsentRecord)
        .filter(
            ConsentRecord.patient_id == patient_id,
            ConsentRecord.consent_type == consent_type,
        )
        .order_by(ConsentRecord.captured_at.desc())
        .first()
    )


def get_patient_consents(db, patient_email: str):
    patient = db.query(Patient).filter(Patient.email == patient_email).first()
    if not patient:
        return {"error": "Patient not found"}

    consents = (
        db.query(ConsentRecord)
        .filter(ConsentRecord.patient_id == patient.id)
        .order_by(ConsentRecord.captured_at.desc())
        .all()
    )

    return {
        "patient_email": patient.email,
        "consents": [
            {
                "consent_id": consent.id,
                "consent_type": consent.consent_type,
                "granted": consent.granted,
                "captured_by": consent.captured_by,
                "source": consent.source,
                "notes": consent.notes,
                "captured_at": consent.captured_at.isoformat(),
            }
            for consent in consents
        ],
    }
