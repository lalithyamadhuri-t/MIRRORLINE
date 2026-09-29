# MIRRORLINE

## The AI that knows when its own knowledge is becoming wrong.

MIRRORLINE is a full-stack AI-agent prototype for the Hindsight hackathon.
It learns beliefs from historical experiences, checks those beliefs against
new evidence, detects knowledge drift, and creates versioned revisions while
preserving the evidence trail.

## What is included

- React + TypeScript + Vite web application
- FastAPI backend
- Hindsight memory abstraction
- Official Hindsight Python client adapter
- Local deterministic fallback for development
- Experience ingestion
- Belief discovery
- Contradiction detection
- Knowledge drift detection
- Belief validation
- Belief versioning
- Scenario analysis
- Deterministic payment-migration demo
- Synthetic dataset generator
- Ground-truth evaluation data
- Evaluation script
- Dockerfiles
- Docker Compose
- Windows PowerShell startup scripts
- Backend smoke tests
- Architecture and demo documentation

## Hindsight

The current Hindsight Python client exposes `retain`, `recall`, and `reflect`,
and the async forms `aretain`, `arecall`, and `areflect`. MIRRORLINE's
`HindsightAdapter` uses the async forms when a Hindsight server is configured.

Official documentation:
https://hindsight.vectorize.io/

Official repository:
https://github.com/vectorize-io/hindsight

## Run locally on Windows

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

Open another PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

Backend API docs:
`http://localhost:8000/docs`

### 3. Run the demo

Click **Run Demo**.

## Optional Hindsight server

Copy `.env.example` to `.env` and configure:

```text
HINDSIGHT_URL=http://localhost:8888
HINDSIGHT_API_KEY=
HINDSIGHT_BANK_ID=mirrorline-demo
```

The official client adapter will then use Hindsight for retain/recall/reflect.

## Generate data

```powershell
python data/generate_dataset.py
```

## Evaluate the seeded dataset

```powershell
python evaluation/evaluate.py
```

## Docker

```powershell
docker compose up --build
```

For a local Hindsight server as well:

```powershell
docker compose -f docker-compose.local.yml up --build
```

## Important

The project is intentionally transparent about what is deterministic and what
requires an external Hindsight/LLM service. Do not claim benchmark results
until the evaluation scripts have actually produced them.
