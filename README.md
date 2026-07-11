# 🏟️ MatchDay Command Center

An accessible, GenAI-powered smart stadium operations and tournament experience web application designed to support fans, organizers, and venue staff during the FIFA World Cup 2026. The platform provides real-time crowd intelligence, multilingual AI-driven fan assistance, accessible wayfinding, and operational decision support.

Built with a **Python (FastAPI)** backend and a **React (TypeScript)** frontend, it integrates **Google Gemini (Vertex AI)** for intelligent insights, uses **Cloud Firestore** for action and snapshot persistence, and is packaged for easy deployment to **Google Cloud Run**.

---

## 🔗 Project Overview

The application is structured around four key user journeys:
1. **Multilingual Fan Assistance:** Interact with a GenAI chatbot responding in 12+ languages with MetLife Stadium-specific knowledge (and deterministic rules fallback).
2. **Interactive Venue Navigation:** Get step-by-step directions with accessibility routing (wheelchair routes, sensory rooms, elevators) and real-time alerts.
3. **Live Crowd Intelligence:** Monitor zone occupancy densities via a real-time heatmap to avoid bottlenecks and manage crowd flow.
4. **Operational Command:** Receive AI-generated, severity-tagged recommendations with one-click action logging for stadium organizers and staff.

---

## 🏗️ Architecture

```text
               +-------------------------------------------------+
               |             React + TypeScript SPA              |
               |  - Accessible HTML & semantic ARIA structures   |
               |  - Dual view: Fan assistant & Ops dashboard     |
               +-----------------------+-------------------------+
                                       |
                                  HTTP (JSON)
                                       |
                                       v
               +-------------------------------------------------+
               |              FastAPI Backend App                |
               |  - Pydantic models with schema validation       |
               |  - Rate limiting & security middlewares         |
               +----------+---------------------------+----------+
                          |                           |
                          v                           v
             +-------------------------+ +-------------------------+
             |    Vertex AI Gemini     | |     Cloud Firestore     |
             |  (Chat & Ops Advisor)   | |   (Snapshot Persistence) |
             |   [Rules-based Fallback]| |    [Memory Repository]  |
             +-------------------------+ +-------------------------+
```

### Layout
- `backend/`: API services, advisor engine, rules engine, database repositories, crowd simulator, and test suites.
- `frontend/`: React components, custom hooks, styles (WCAG AA), type definitions, and component/accessibility tests.
- `docs/`: In-depth documentation regarding internal structures and design choices.

---

## 🚀 Local Development Setup

### Prerequisite Environment
- Python 3.11 or newer
- Node.js 20 or newer

### 1. Running the Backend
From the repository root:
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Start the local server with Gemini and Firestore mock integrations active:
```bash
USE_GEMINI=false USE_FIRESTORE=false uvicorn app.main:app --reload --port 8000
```
The API documentation will be available at `http://localhost:8000/docs`.

### 2. Running the Frontend
From the repository root:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` (requests under `/api/*` are proxied to the backend at `http://localhost:8000`).

### 3. Containerized Execution
Build and run the entire application as a single Docker container locally:
```bash
docker build -t matchday-command-center .
docker run -p 8000:8000 -e USE_GEMINI=false -e USE_FIRESTORE=false matchday-command-center
```
Then visit `http://localhost:8000`.

---

## 🧪 Testing and Quality Control

All quality checks are enforced automatically on every commit and push:

| Test Suite | Execution | Targets |
|---|---|---|
| **Backend Tests** | `cd backend && pytest --cov=app --cov-fail-under=90` | Crowd engine formulas, Firestore/memory integrations, routing schema validation, Gemini parsing, and fallback rules. |
| **Frontend Tests** | `cd frontend && npm run test` | React components, API integrations, hooks, and axe accessibility audits. |
| **Linting** | `ruff check .` / `npm run lint` | Strict quality guidelines (including `jsx-a11y` constraints). |
| **Static Types** | `mypy app` / `npm run build` | Strict compiler verification in Python (mypy) and TypeScript (tsc). |

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
