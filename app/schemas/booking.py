from pydantic import BaseModel

class BookingRequest(BaseModel):
    patient_name: str
    doctor_specialization: str
    time: str


class BookingResponse(BaseModel):
    message: str
    appointment_id: int