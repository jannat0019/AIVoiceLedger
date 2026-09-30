# VoiceLedger

VoiceLedger is a multimodal AI expense tracker that lets users record expenses using receipt images and voice input.

The project is being built as a production-style full-stack AI application using:

Frontend: Next.js, React, TypeScript, Tailwind CSS
Backend: FastAPI, Python
Database & Auth: Supabase
Vision AI:Groq vision model
Speech-to-Text: Groq Whisper
Validation: Pydantic

## Current Progress

### Receipt Extraction

The first working pipeline is:

```text
Receipt Image
     ↓
FastAPI
     ↓
Vision LLM
     ↓
JSON Extraction
     ↓
Pydantic Validation
     ↓
Validated ExpenseDraft
```



## Project Structure

```text
voiceledger/
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── vision.py
│   ├── test_vision.py
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│
├── evals/
│
└── README.md
```

## Running the Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --reload


## Planned Features

* Receipt image extraction
* Human review and confirmation
* Supabase expense storage
* User authentication
* Voice expense entry
* Expense dashboard and analytics
* Natural-language expense queries
* Duplicate expense detection
* AI extraction evaluations
* Automated tests
* Docker and CI/CD
* Cloud deployment