install:
	pip install -e ../aws ../types -e .

export_env:
	export $$(grep -v '^#' .env.local | xargs)

run: export_env
	uvicorn tta_service.main:app --reload --port 8000
