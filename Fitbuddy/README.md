# FitBuddy

A FastAPI fitness planner with SQLite persistence and optional Gemini-powered workout generation. Set `DEMO_MODE=true` to use built-in sample plans without a Google API key.

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

On Linux or macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `GOOGLE_API_KEY` in `.env` to enable Gemini generation. Set a private `ADMIN_KEY` before deployment.

## Run

Use `run_windows.bat` on Windows or `./run_linux.sh` on Linux. You can also run `python -m uvicorn app.main:app --reload` from the project root. The home page is at `/`, and `/health` returns a basic status response.

## Tests

Run `python -m unittest discover -s tests`.