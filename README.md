
# PathCraft: AI-Powered Goal Decomposition & Scheduling App

PathCraft is an AI-powered productivity platform that helps users break down big goals, schedule tasks intelligently, and stay on track with adaptive reminders. It supports both individual and team productivity, with a vision for deep integrations and smart coaching.

---

## 🚀 Project Vision

Empower users to achieve complex goals by:
- Decomposing goals into actionable sub-goals and tasks
- Scheduling tasks optimally using AI
- Providing adaptive reminders and notifications
- Supporting team OKRs and integrations with popular platforms

---

## 🗂️ Project Structure

- `backend/` — FastAPI application for all core services (API, DB, scheduling, notifications, etc.)
- `frontend/` — Flutter mobile app (UI, widgets, user flows)
- `ml/` — Machine learning models and scripts for scheduling and reminders
- `database/` — Database schemas and Alembic migrations
- `tests/` — Automated backend tests (pytest, FastAPI TestClient)
- `wireframes/` — UI/UX design docs and wireframes
- `prototype/` — Early web prototype (HTML/JS/CSS)

---

## ✨ Key Features

### Implemented
- **Goal Management:** Create, decompose, and manage goals, sub-goals, and tasks
- **Freemium Model:** Free users limited to 3 active goals
- **Intelligent Scheduling (Placeholder):** Suggests optimal time slots for tasks
- **Adaptive Reminders (Placeholder):** Suggests reminder frequency for tasks
- **Notifications:** Email and push notifications for tasks and reminders
- **Recurring Tasks:** Support for daily/weekly recurring tasks
- **Calendar Integrations:** Google/Outlook calendar integration endpoints
- **Comprehensive API Tests:** Automated tests for all major backend endpoints

### Planned / In Progress
- **Full AI Scheduling:** ML model predicts best time slots based on user behavior
- **Full Adaptive Reminders:** ML model personalizes reminders
- **Team Features:** Team OKRs, shared goals, Slack/Teams bots
- **Learning Platform Integrations:** HR/learning platform sync
- **Wearable & Contextual Integrations:** Biofeedback, location, AR vision board
- **Generative Chat Coach:** AI chat for productivity coaching

---

## 🛠️ Setup & Run Instructions

### 1. Backend (FastAPI)

**Requirements:** Python 3.10+, pip

**Install dependencies:**
```sh
pip install -r backend/requirements.txt
pip install python-multipart pytest
```

**Environment:**
- Copy `.env.example` to `.env` in the project root and fill in secrets (if needed)

**Run the server:**
```sh
uvicorn backend.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

**Database:**
- Uses SQLite by default (`pathcraft.db` for app, `test.db` for tests)
- Alembic migrations in `database/migrations/`

**API Reference:**
- See `backend/API_REFERENCE.md` for endpoints

### 2. Frontend (Flutter)

**Requirements:** Flutter SDK, Dart

**Setup:**
- Navigate to `frontend/` and run:
	```sh
	flutter pub get
	flutter run
	```
- The main app code is in `frontend/lib/`

### 3. Machine Learning (ML)

**Requirements:** Python 3.10+, pip, scikit-learn, pandas, etc.

**Setup:**
- Navigate to `ml/` and install any extra requirements as needed
- Scripts for training and data generation are in `ml/`

---

## 🧪 Running Tests

### Backend Tests
From the project root:
```sh
pytest
```
or to run a specific test file:
```sh
pytest tests/test_backend.py
```
Tests use a temporary SQLite database (`test.db`).

### Frontend & ML Tests
- (Planned) Add tests for Flutter and ML modules

---

## 📦 Environment & Files

- `.env`, `.db`, and other sensitive/generated files are git-ignored (see `.gitignore`)
- Virtual environments (`.venv/`, `env/`) and IDE files are ignored

---

## 🤝 Contributing

1. Fork and clone the repo
2. Create a new branch for your feature/fix
3. Add tests for new features
4. Open a pull request with a clear description

---

## 🛟 Troubleshooting

- If you see `ModuleNotFoundError` for `backend`, set `PYTHONPATH` to the project root:
	```sh
	set PYTHONPATH=%cd%  # Windows
	export PYTHONPATH=$(pwd)  # macOS/Linux
	```
- If you see `RuntimeError: Form data requires "python-multipart"`, install it:
	```sh
	pip install python-multipart
	```
- For database errors, delete `test.db` and rerun tests

---

## 📄 Documentation

- See `wireframes/` for UI/UX docs
- See `backend/API_REFERENCE.md` for API details
- See `implementation_log.pdf` for implementation notes

---

## License

MIT License (see `LICENSE` file)
