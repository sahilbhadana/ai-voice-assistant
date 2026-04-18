from pydantic import BaseModel
from typing import Optional

class BookingRequest(BaseModel):
    patient_name: str
    patient_email: str
    patient_phone: Optional[str] = None
    doctor_specialization: str
    time: str


class CancelRequest(BaseModel):
    appointment_id: int


class RescheduleRequest(BaseModel):
    appointment_id: int
    new_time: str


class HistoryRequest(BaseModel):
    patient_email: str


class BookingResponse(BaseModel):
    message: str
    appointment_id: int