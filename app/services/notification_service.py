import logging
import os

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")


def _get_twilio_client():
    try:
        from twilio.rest import Client
    except ImportError:
        logger.error("Twilio package is not installed. Install 'twilio' to send messages.")
        return None

    if TWILIO_ACCOUNT_SID == "your_account_sid" or TWILIO_AUTH_TOKEN == "your_auth_token":
        logger.error("Twilio credentials are not configured.")
        return None

    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_sms(to_number: str, message: str) -> bool:
    client = _get_twilio_client()
    if not client:
        return False

    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number,
        )
        logger.info("SMS sent to %s", to_number)
        return True
    except Exception as e:
        logger.error("Failed to send SMS to %s: %s", to_number, str(e))
        return False


def send_whatsapp_message(to_number: str, message: str) -> bool:
    client = _get_twilio_client()
    if not client:
        return False

    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_number}",
        )
        logger.info("WhatsApp message sent to %s", to_number)
        return True
    except Exception as e:
        logger.error("Failed to send WhatsApp message to %s: %s", to_number, str(e))
        return False


def build_sms_message(
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: str,
    language: str = "en",
) -> str:
    if language == "hi":
        return (
            f"Namaste {patient_name}, your appointment with Dr. {doctor_name} is confirmed for "
            f"{appointment_date} at {appointment_time}. Confirmation ID: {appointment_id}."
        )

    return (
        f"Hi {patient_name}, your appointment with Dr. {doctor_name} is confirmed for "
        f"{appointment_date} at {appointment_time}. Confirmation ID: {appointment_id}."
    )


def build_reminder_message(
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    appointment_id: str,
    hours_ahead: int,
    language: str = "en",
) -> str:
    if language == "hi":
        return (
            f"Namaste {patient_name}, this is a reminder that your appointment with Dr. {doctor_name} "
            f"is in the next {hours_ahead} hours: {appointment_date} at {appointment_time}. "
            f"Confirmation ID: {appointment_id}."
        )

    return (
        f"Hi {patient_name}, this is a reminder that your appointment with Dr. {doctor_name} "
        f"is in the next {hours_ahead} hours: {appointment_date} at {appointment_time}. "
        f"Confirmation ID: {appointment_id}."
    )
