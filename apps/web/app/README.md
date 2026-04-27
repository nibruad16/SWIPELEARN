# @swipelearn/api

FastAPI server — the thin orchestration layer that exposes REST endpoints.

## Dependencies
- `swipelearn-core`: Shared models
- `swipelearn-services`: Business logic

## Run

```bash
cd packages/api
pip install -r requirements.txt
pip install -e ../core
pip install -e ../services
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`
