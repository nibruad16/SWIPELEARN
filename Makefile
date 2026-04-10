.PHONY: install dev test lint docker-up docker-down

# ─── Install ──────────────────────────────────────────────────────────
install:
	pip install -e packages/core
	pip install -e packages/services
	pip install -r packages/api/requirements.txt
	cd packages/mobile && flutter pub get

# ─── Dev ──────────────────────────────────────────────────────────────
dev-api:
	cd packages/api && uvicorn app.main:app --reload

dev-mobile:
	cd packages/mobile && flutter run

# ─── Test ─────────────────────────────────────────────────────────────
test:
	cd packages/api && pytest tests/ -v

# ─── Docker ───────────────────────────────────────────────────────────
docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
