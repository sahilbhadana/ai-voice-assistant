# 🧠 AI-Powered Conversational Appointment Booking System

A **stateful, AI-driven backend system** that enables users to book medical appointments using natural language.
The system leverages a local LLM to understand user intent, maintains conversational context across multiple turns, and executes real-time booking workflows with intelligent fallback handling.

---

# 🚀 Features

## ✅ Multi-Language Support (English/Hindi)

- **Language Selection**: Users can choose their preferred language at the start of conversation
  - Press `1` for English
  - Press `2` for हिंदी (Hindi)

- **Bilingual Responses**: All system responses are provided in the selected language
- **Hindi Email Templates**: Confirmation emails are sent in Hindi for Hindi-speaking users
- **Intelligent Prompts**: LLM receives language-specific prompts for better understanding

**Example Conversation Flow:**

```
Bot: Please select your language:
     1. English
     2. हिंदी (Hindi)

User: 2
Bot: धन्यवाद! आपका नाम क्या है?

User: राहुल कुमार
Bot: धन्यवाद! आपका ईमेल पता क्या है?

User: rahul@example.com
Bot: बेहतरीन! आपको किस डॉक्टर की विशेषज्ञता चाहिए?
```

---

## ✅ Natural Language Understanding

- Users can interact using free-form text:
  - _“Book appointment with cardiologist at 10”_
  - _“Cardiologist”_
  - _“yes”_

- Uses local LLM (**Llama 3 via Ollama**) to extract structured data.

---

## ✅ Multi-Turn Conversational Memory

- Maintains session-based context using `session_id`
- Supports step-by-step interactions:

  ```
  User: Book appointment
  Bot: Which doctor specialization?

  User: Cardiologist
  Bot: What time?

  User: 10
  Bot: Appointment booked
  ```

---

## ✅ Intelligent Decision Engine

- Dynamically determines next step:
  - Ask missing information
  - Proceed to booking

- Ensures smooth conversational flow

---

## ✅ Smart Fallback Handling

- If requested slot is unavailable:

  ```
  "10:00 is not available. Available slots: 11:00, 12:00"
  ```

- Allows user to:
  - select slot → `"12"`
  - approve suggestion → `"yes"`, `"ok"`

---

## ✅ Intelligent Time Preference Selection

- Users can choose appointment times using smart preferences:
  - **"earliest available"** → Books the earliest available slot
  - **"morning"** → Filters slots between 6 AM - 12 PM
  - **"afternoon"** → Filters slots between 12 PM - 6 PM
  - **"any time"** → Shows all available slots

- Example conversation:

  ```
  User: Book appointment with cardiologist
  Bot: Which doctor specialization do you need?

  User: Cardiologist
  Bot: How would you like to choose your appointment time?
       Options: earliest available, any time, morning, afternoon

  User: Morning
  Bot: Please select a specific time or confirm a suggestion.

  User: 10:00
  Bot: Your appointment is booked!
  ```

---

## ✅ Automated Email Notifications

- **Booking Confirmation** ✉️
  - Sent immediately after appointment is booked
  - Contains: Doctor name, date, time, location, confirmation ID
  - Proof of booking for patient

- **24-Hour Reminder** 📅
  - Auto-sent 24 hours before appointment
  - Reminds patient to prepare
  - Shows all appointment details

- **1-Hour Reminder** ⏰
  - Auto-sent 1 hour before appointment
  - Urgent reminder to leave for hospital
  - No-show prevention

- **No-Show Follow-up** 📧
  - Auto-sent if patient doesn't show up
  - Encourages rescheduling
  - Tracks no-show history

- **Cancellation Confirmation** ❌
  - Sent when appointment is cancelled
  - Releases slot back to availability
  - Option to reschedule

**Features:**

- Beautiful HTML email templates
- Plain text fallback for all email clients
- SMTP integration with Gmail, SendGrid, AWS SES, etc.
- Contact information captured during booking
- Email preferences tracking

---

## ✅ Patient Profile Management

- Collects patient information during voice call:
  - Full name
  - Email address
  - Phone number (from caller ID)

- Stores patient profile in database
- Tracks appointment history per patient
- Enables personalized communication

---

## ✅ Context-Aware Recovery

- Stores suggested slots in session
- Handles follow-up inputs intelligently
- Continues conversation seamlessly

---

## ✅ Database-Driven Booking

- Uses **PostgreSQL** for:
  - doctors
  - slots
  - appointments
  - **patients** (NEW)

- Real-time validation of availability
- Full schedule support (10 AM - 8 PM)
- Patient history tracking

---

## ✅ Robust Error Handling

- Prevents false success responses
- Validates booking results before responding
- Gracefully handles edge cases
- Email sending failures don't block booking

---

# 🧠 System Architecture

```
User Input
   ↓
FastAPI (API Layer)
   ↓
Conversation Service
   ↓
LLM (Llama 3 via Ollama)
   ↓
State Manager (Session Memory)
   ↓
Decision Engine
   ↓
Booking Service
   ↓
PostgreSQL Database
   ↓
Response
```

---

# 🧱 Tech Stack

## Backend

- FastAPI
- Python

## AI / NLP

- Ollama
- Llama 3

## Database

- PostgreSQL

## ORM

- SQLAlchemy

---

# ⚙️ Installation & Setup

## 1. Clone Repository

```bash
git clone <your-repo-url>
cd ai-voice-assistant
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Setup PostgreSQL

- Create database
- Update connection string in `database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
```

---

## 5. Configure Email Notifications

Create `.env` file in project root:

```bash
# Copy the example
cp .env.example .env

# Edit .env with your email credentials
```

**Email Configuration Options:**

### Option A: Gmail (Recommended for Testing)

```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password  # Use App Password, not regular password
SENDER_NAME=City Hospital
```

**Setup Gmail App Password:**

1. Enable 2-Factor Authentication on Gmail
2. Go to myaccount.google.com → Security → App passwords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character password
5. Use it as `SENDER_PASSWORD` in `.env`

### Option B: SendGrid

```
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey  # Keep as "apikey"
SENDER_PASSWORD=SG.xxxxx...  # Your SendGrid API key
SENDER_NAME=City Hospital
```

### Option C: AWS SES

```
SMTP_SERVER=email-smtp.region.amazonaws.com
SMTP_PORT=587
SENDER_EMAIL=your-verified-email@domain.com
SENDER_PASSWORD=your-smtp-password
SENDER_NAME=City Hospital
```

---

## 6. Run Migrations / Create Tables

```bash
uvicorn app.main:app --reload
```

---

## 7. Seed Database

```bash
python -m app.db.seed
```

---

## 8. Run Ollama

```bash
ollama run llama3
```

---

## 9. Start Server

```bash
uvicorn app.main:app --reload
```

---

# 🧪 API Usage

## Base URL

```
http://127.0.0.1:8000/docs
```

---

## 🔹 Endpoint: `/chat`

### Request:

```json
{
  "session_id": "user1",
  "text": "Book cardiologist at 10"
}
```

---

## 🔹 Complete Example Flow (With Email Notifications)

### Step 1: Start Conversation

```json
Request: {
  "session_id": "user-001",
  "text": "Book appointment"
}

Response: "Thank you! What's your email address?"
```

### Step 2: Collect Patient Email

```json
Request: {
  "session_id": "user-001",
  "text": "john@example.com"
}

Response: "Great! Which doctor specialization do you need?"
```

### Step 3: Select Doctor Specialization

```json
Request: {
  "session_id": "user-001",
  "text": "Cardiologist"
}

Response: {
  "response": "How would you like to choose your appointment time?",
  "options": ["earliest available", "any time", "morning", "afternoon"],
  "follow_up": "Or specify a specific time like '10 AM'"
}
```

### Step 4: Choose Time Preference

```json
Request: {
  "session_id": "user-001",
  "text": "Morning"
}

Response: "Please select a specific time or confirm a suggestion."
```

### Step 5: Confirm Appointment Time

```json
Request: {
  "session_id": "user-001",
  "text": "10:00"
}

Response: {
  "response": "Your appointment is booked! A confirmation email has been sent to your address.",
  "booking_result": {
    "appointment_id": "APT-123",
    "appointment": {
      "doctor_name": "Dr. Sharma",
      "appointment_date": "2025-04-15",
      "appointment_time": "10:00",
      "status": "booked"
    }
  }
}
```

### � New Scheduling API Endpoints

- `GET /availability?specialization=<specialization>` — returns all slots and availability for a doctor specialization
- `GET /slots?specialization=<specialization>` — returns currently available slots only
- `POST /history` — retrieve appointment history for a patient email
- `POST /cancel` — cancel an existing appointment by `appointment_id`
- `POST /reschedule` — reschedule an existing appointment by `appointment_id` and `new_time`

#### Example: Availability

```http
GET /availability?specialization=cardiologist
```

#### Example: Appointment History

```json
POST /history
{
  "patient_email": "john@example.com"
}
```

#### Example: Cancel Appointment

```json
POST /cancel
{
  "appointment_id": 123
}
```

#### Example: Reschedule Appointment

```json
POST /reschedule
{
  "appointment_id": 123,
  "new_time": "14:00"
}
```

### �📧 Automatic Emails Sent:

1. **Immediate:** Booking Confirmation
   - Contains appointment details
   - Confirmation ID for reference
2. **24 Hours Before:** Reminder Email
   - "Your appointment is tomorrow!"
   - Encourages early arrival
3. **1 Hour Before:** Urgent Reminder
   - Final notification
   - Reduces no-shows
4. **If No-Show:** Follow-up Email
   - Encourages rescheduling
   - Tracks attendance

---

## 🔹 Language Selection Feature

### English Flow Example:

```json
// Step 1: Language Selection
Request: {
  "session_id": "user-en",
  "text": "1"
}

Response: "Thank you! What's your name?"

// Step 2: Name
Request: {
  "session_id": "user-en",
  "text": "John Doe"
}

Response: "Thank you! What's your email address?"

// Continue with normal English flow...
```

### Hindi Flow Example:

```json
// Step 1: Language Selection
Request: {
  "session_id": "user-hi",
  "text": "2"
}

Response: "धन्यवाद! आपका नाम क्या है?"

// Step 2: Name
Request: {
  "session_id": "user-hi",
  "text": "राहुल कुमार"
}

Response: "धन्यवाद! आपका ईमेल पता क्या है?"

// Step 3: Email
Request: {
  "session_id": "user-hi",
  "text": "rahul@example.com"
}

Response: "बेहतरीन! आपको किस डॉक्टर की विशेषज्ञता चाहिए?"

// Continue with normal Hindi flow...
```

**Note:** Hindi users will receive confirmation emails in Hindi with appropriate formatting and content.

---

## 🔹 Example Legacy Flow (Simple)

### Step 1:

```json
"Book appointment"
```

→

```json
"Which doctor specialization do you need?"
```

---

### Step 2:

```json
"Cardiologist"
```

→

```json
"What time would you prefer?"
```

---

### Step 3:

```json
"10"
```

→

```json
"Your appointment is booked!"
```

---

## 🔹 Fallback Example

```json
"Book cardiologist at 10"
```

→

```json
"10:00 is not available. Available slots: 11:00, 12:00"
```

---

### Follow-up:

```json
"yes"
```

→

```json
"Your appointment is booked!"
```

---

# 🧠 Key Challenges & Solutions

---

## 1. LLM Output Unreliable

### Problem:

- Non-JSON output
- Hallucinated fields

### Solution:

- Strict prompt engineering
- JSON validation + fallback parsing

---

## 2. Stateless API Limitation

### Problem:

- Conversation context lost

### Solution:

- Session-based memory using in-memory store

---

## 3. Incorrect System Responses

### Problem:

- False success messages

### Solution:

- Explicit error handling in booking pipeline

---

## 4. Poor UX on Failure

### Problem:

```
"No slot available"
```

### Solution:

- Suggest alternative slots dynamically

---

## 5. No Contextual Follow-up

### Problem:

- System didn’t understand:

```
"12"
```

### Solution:

- Stored `suggested_slots`
- Context-aware mapping

---

## 6. Natural Language Variations

### Problem:

```
"Yes" vs "yes" vs "OK"
```

### Solution:

```python
text.strip().lower()
```

---

## 7. Performance Constraints

### Problem:

- Slow LLM responses

### Solution:

- Identified bottleneck
- Designed optimization strategies (future improvements)

---

## 8. Email Notifications Not Sending

### Problem:

- Emails not received
- "Connection refused" or "Authentication failed"

### Solution:

**Check SMTP Configuration:**

```bash
# Verify .env file exists and is configured
cat .env

# Test email sending with Python
python -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    print('✅ Email configuration is correct!')
    server.quit()
except Exception as e:
    print(f'❌ Error: {e}')
"
```

**Common Issues & Fixes:**

| Issue                 | Cause             | Fix                                          |
| --------------------- | ----------------- | -------------------------------------------- |
| Authentication failed | Wrong password    | Use Gmail App Password, not regular password |
| Connection refused    | Firewall blocking | Ensure SMTP_PORT 587 is open                 |
| Timeout               | Network issue     | Check internet connection                    |
| "Less secure apps"    | Gmail security    | Enable 2FA and use App Password              |
| Email not received    | Wrong recipient   | Verify patient email is correct              |

**Enable Logging:**

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Check logs for email errors
```

---

# 🚀 Future Improvements

- SMS notifications (Twilio integration)
- Appointment cancellation/rescheduling
- Doctor availability management
- Patient ratings and reviews
- Advanced analytics dashboard
- Redis-based session storage
- Async LLM calls
- Voice interface integration
- Frontend UI (React/Vue)
- Deployment (Docker + AWS/GCP)

---

# 🧠 Key Learnings

- **Conversational AI:** LLMs require strict validation and prompt engineering
- **State Management:** Essential for multi-turn conversations
- **Error Handling:** Backend must gracefully handle failures
- **Email Integration:** Critical for user engagement and no-show reduction
- **Data Persistence:** Session storage maintains conversation context
- **Email Templates:** Beautiful, responsive HTML emails improve user trust
- **Performance:** Optimizing LLM calls and database queries is crucial
- **User Experience:** Confirmation and reminders significantly increase show-ups

---

# 💼 Resume Highlight

> Built a stateful conversational AI voice booking system integrating:
>
> - LLM-based natural language intent extraction (Llama 3)
> - Multi-turn contextual conversation management
> - Intelligent time preference filtering
> - Automated email notification system (confirmation, reminders, follow-ups)
> - Patient profile management and history tracking
> - Real-time availability checking with race condition prevention

---

# 📌 Author

**Sahil Bhadana**
