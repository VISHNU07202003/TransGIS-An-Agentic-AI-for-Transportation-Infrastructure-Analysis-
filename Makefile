db-up:
	docker compose up -d db

db-down:
	docker compose down

db-reset:
	docker compose down -v && docker compose up -d db

backend-install:
	cd backend && pip install -r requirements.txt

backend-run:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev

test:
	cd backend && pytest -v

discover-fdot:
	cd scripts && python discover_fdot_layers.py

discover-gainesville:
	cd scripts && python inspect_gainesville_dataset.py

health:
	cd scripts && python health_check.py
