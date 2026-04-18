# AI Voice Assistant Appointment Booking API

A FastAPI backend for conversational medical appointment booking. The system supports multi-turn chat, local LLM intent extraction, date-aware scheduling, patient profiles, notification consent, SMS/email notifications, staff operations, external system sync, audit logging, and demand analytics.

## Features

- Conversational booking flow with session memory
- English/Hindi response support in the chat flow
- LLM-based intent extraction with Ollama/Llama 3
- Date-aware doctor availability and appointment booking
- Patient profile and appointment history tracking
- Signed bearer-token authentication
- Role-based access control for staff operations
- Session locking for staff review
- Consent capture for booking notifications
- Email confirmations and Twilio SMS reminders
- Signed appointment action tokens for cancel/reschedule flows
- EHR/calendar webhook sync with retry metadata
- Demand analytics and reporting
- Audit logs for sensitive staff actions
- Alembic migration scaffolding
- Optional background SMS reminder scheduler

## Tech Stack

- FastAPI
- Python
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Twilio
- Ollama/Llama 3

## Setup

### 1. Clone And Install

```bash
git clone <your-repo-url>
cd ai-voice-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example file:

```bash
cp .env.example .env
```

Important environment variables:

```bash
DATABASE_URL=postgresql://postgres:password@localhost/hospital_ai
APP_SECRET_KEY=replace-with-a-long-random-secret
AUTH_TOKEN_TTL_SECONDS=86400
PUBLIC_API_BASE_URL=http://127.0.0.1:8000

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=City Hospital

TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

EHR_WEBHOOK_URL=
CALENDAR_WEBHOOK_URL=

ENABLE_REMINDER_SCHEDULER=false
REMINDER_SCHEDULER_INTERVAL_SECONDS=300
REMINDER_WINDOW_MINUTES=1440
```

### 3. Database

For a new local database, the app still runs `Base.metadata.create_all()` on startup.

For existing databases or production-style schema changes, use Alembic:

```bash
alembic upgrade head
```

### 4. Start Ollama

```bash
ollama run llama3
```

### 5. Start API

```bash
uvicorn app.main:app --reload
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Authentication

The API uses signed bearer tokens. Passwords are stored with PBKDF2 hashes.

Roles:

- `admin`
- `receptionist`
- `doctor`
- `patient`
- `analyst`

Bootstrap behavior:

- If no users exist, `POST /auth/register` can create the first user with any valid role.
- After users exist, public registration can only create `patient` users.
- Staff users must be created by an authenticated admin through `POST /auth/users`.

### Register

```json
POST /auth/register
{
  "name": "Sahil",
  "email": "sahil@example.com",
  "password": "strong-password",
  "role": "admin"
}
```

### Login

```json
POST /auth/login
{
  "email": "sahil@example.com",
  "password": "strong-password"
}
```

Use the returned token:

```http
Authorization: Bearer <access_token>
```

### Current User

```http
GET /auth/me
Authorization: Bearer <access_token>
```

## Booking

### Book Appointment

Requires role: `admin`, `receptionist`, or `patient`.

```json
POST /book
Authorization: Bearer <access_token>
{
  "patient_name": "John Doe",
  "patient_email": "john@example.com",
  "patient_phone": "+15551234567",
  "doctor_specialization": "cardiologist",
  "date": "2026-04-22",
  "time": "10:00",
  "consent_granted": true,
  "consent_notes": "Patient agreed to SMS reminders"
}
```

Response includes signed action tokens:

```json
{
  "message": "Appointment booked",
  "appointment_id": "APT-123",
  "appointment": {
    "id": 123,
    "doctor_name": "Dr. Sharma",
    "appointment_date": "2026-04-22",
    "appointment_time": "10:00",
    "status": "booked"
  },
  "actions": {
    "cancel_token": "...",
    "reschedule_token": "..."
  }
}
```

### Availability

```http
GET /availability?specialization=cardiologist&date=2026-04-22
```

### Slots

```http
GET /slots?specialization=cardiologist&date=2026-04-22
```

### History

Requires role: `admin`, `receptionist`, `doctor`, or `patient`.

```json
POST /history
Authorization: Bearer <access_token>
{
  "patient_email": "john@example.com"
}
```

### Cancel

Requires role: `admin`, `receptionist`, or `doctor`.

```json
POST /cancel
Authorization: Bearer <access_token>
{
  "appointment_id": 123
}
```

### Reschedule

Requires role: `admin`, `receptionist`, or `doctor`.

```json
POST /reschedule
Authorization: Bearer <access_token>
{
  "appointment_id": 123,
  "new_date": "2026-04-23",
  "new_time": "14:00"
}
```

### Signed Appointment Actions

Patients can use signed tokens from the booking response.

Cancel with a token:

```http
GET /appointments/cancel/{token}
```

Reschedule with a token:

```json
POST /appointments/action
{
  "token": "<reschedule_token>",
  "new_date": "2026-04-23",
  "new_time": "14:00"
}
```

## Conversational Chat

The `/chat` route keeps an in-memory session and walks the patient through language selection, name, email, phone, specialization, and time selection.

```json
POST /chat
{
  "session_id": "user-001",
  "text": "Book appointment"
}
```

Session locks can pause a conversation while staff reviews it.

## Consent Capture

Notification consent is recorded during booking and can also be managed directly.

Requires role: `admin`, `receptionist`, or `doctor`.

```json
POST /consents
Authorization: Bearer <access_token>
{
  "patient_email": "john@example.com",
  "consent_type": "booking_notifications",
  "granted": true,
  "captured_by": "front-desk",
  "source": "phone",
  "notes": "Patient agreed verbally"
}
```

View consent history:

```http
GET /consents/john@example.com
Authorization: Bearer <access_token>
```

SMS reminders check the latest `booking_notifications` consent before sending.

## Session Locking

Requires role: `admin`, `receptionist`, or `doctor`.

```json
POST /sessions/lock
Authorization: Bearer <access_token>
{
  "session_id": "user-001",
  "locked_by": "front-desk",
  "reason": "Manual review"
}
```

```http
GET /sessions/user-001/lock
POST /sessions/user-001/unlock
```

When a session is locked, the chat route returns a lock message instead of mutating session state.

## Notifications

### Manual SMS Reminder Dispatch

Requires role: `admin` or `receptionist`.

```http
POST /notifications/reminders?minutes_ahead=1440
Authorization: Bearer <access_token>
```

### Optional Scheduler

Enable automatic reminder scans:

```bash
ENABLE_REMINDER_SCHEDULER=true
REMINDER_SCHEDULER_INTERVAL_SECONDS=300
REMINDER_WINDOW_MINUTES=1440
```

The scheduler runs in a background daemon thread on app startup.

## EHR And Calendar Integration

The integration service can sync appointments to configured webhooks.

Set:

```bash
EHR_WEBHOOK_URL=https://ehr.example.com/webhook
CALENDAR_WEBHOOK_URL=https://calendar.example.com/webhook
```

Sync appointment:

```json
POST /integrations/sync
Authorization: Bearer <access_token>
{
  "appointment_id": 123,
  "target_system": "all"
}
```

Valid targets:

- `all`
- `ehr`
- `calendar`

View sync history:

```http
GET /integrations/123/history
Authorization: Bearer <access_token>
```

Retry queued or failed syncs:

```http
POST /integrations/retry?limit=20
Authorization: Bearer <access_token>
```

## Analytics

Requires role: `admin` or `analyst`.

```json
POST /analytics/demand
Authorization: Bearer <access_token>
{
  "start_date": "2026-04-01",
  "end_date": "2026-04-30"
}
```

The report includes:

- total appointments
- appointments by status
- appointments by day
- appointments by doctor
- demand by specialization
- slot utilization percentage

## Audit Logs

Requires role: `admin`.

```http
GET /audit/logs?limit=100
Authorization: Bearer <access_token>
```

Audited actions include booking, history access, cancel/reschedule, consent access, session locks, integration syncs, analytics access, and audit log reads.

## AI Booking Endpoints

Extract intent:

```http
POST /ai/extract
```

Book from natural language:

```http
POST /ai/book
```

These endpoints use the LLM service to parse user text into booking fields.

## Operational Notes

- Use `APP_SECRET_KEY` with a long random value before real usage.
- Use Alembic for existing databases because `create_all()` does not add new columns to existing tables.
- Configure Twilio credentials before enabling SMS sends.
- Configure SMTP credentials before relying on email confirmations.
- Keep `ENABLE_REMINDER_SCHEDULER=false` during local testing unless you intentionally want background reminder scans.
- The in-memory session store is simple and resets when the app restarts. Redis would be the next step for production sessions.

## Author

Sahil Bhadana
