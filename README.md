# 🧠 AI-Powered Conversational Appointment Booking System

A **stateful, AI-driven backend system** that enables users to book medical appointments using natural language.
The system leverages a local LLM to understand user intent, maintains conversational context across multiple turns, and executes real-time booking workflows with intelligent fallback handling.

---

# 🚀 Features

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

- Real-time validation of availability
- Full schedule support (10 AM - 8 PM)

---

## ✅ Robust Error Handling

- Prevents false success responses
- Validates booking results before responding
- Gracefully handles edge cases

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

## 5. Run Migrations / Create Tables

```bash
uvicorn app.main:app --reload
```

---

## 6. Seed Database

```bash
python -m app.db.seed
```

---

## 7. Run Ollama

```bash
ollama run llama3
```

---

## 8. Start Server

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

## 🔹 Example Flow

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

# 🚀 Future Improvements

- Redis-based session storage
- Async LLM calls
- Slot ranking (earliest / preferred)
- Voice interface integration
- Frontend UI
- Deployment (Docker + Cloud)

---

# 🧠 Key Learnings

- LLMs require strict validation
- State management is essential for conversational systems
- Backend must handle failure gracefully
- Data consistency is critical
- Performance optimization is architectural

---

# 💼 Resume Highlight

> Built a stateful conversational AI system integrating LLM-based intent extraction with backend workflow execution, featuring multi-turn context management, intelligent fallback handling, and real-time database-driven decision making.

---

# 📌 Author

**Sahil Bhadana**
