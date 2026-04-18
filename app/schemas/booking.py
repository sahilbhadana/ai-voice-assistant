from pydantic import BaseModel
from typing import Optional

class BookingRequest(BaseModel):
    patient_name: str
    patient_email: str
    patient_phone: Optional[str] = None
    doctor_specialization: str
    date: Optional[str] = None
    time: str
    consent_granted: bool = False
    consent_notes: Optional[str] = None


class CancelRequest(BaseModel):
    appointment_id: int


class RescheduleRequest(BaseModel):
    appointment_id: int
    new_time: str
    new_date: Optional[str] = None


class HistoryRequest(BaseModel):
    patient_email: str


class BookingResponse(BaseModel):
    message: str
    appointment_id: int


class ConsentCaptureRequest(BaseModel):
    patient_email: str
    consent_type: str = "booking_notifications"
    granted: bool
    captured_by: str = "system"
    source: str = "api"
    notes: Optional[str] = None


class SessionLockRequest(BaseModel):
    session_id: str
    locked_by: str
    reason: Optional[str] = None


class IntegrationSyncRequest(BaseModel):
    appointment_id: int
    target_system: str = "all"


class AnalyticsRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "patient"


class LoginRequest(BaseModel):
    email: str
    password: str


class AppointmentActionRequest(BaseModel):
    token: str
    new_date: Optional[str] = None
    new_time: Optional[str] = None
