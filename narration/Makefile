install:  # on a Mac: runs the model through MLX
	python3.12 -m venv .venv
	.venv/bin/pip install -r requirements_dev.txt -e ../script -e ".[mlx]"

lint:
	.venv/bin/python -m pylint --rcfile=../.pylintrc tta_narration tests

types:
	.venv/bin/python -m mypy tta_narration tests

test:
	.venv/bin/python -m pytest tests

worker:  # runs one job locally: make worker JOB=job.json
	.venv/bin/python -m tta_narration.worker --test_input "$$(cat $(JOB))"

image:
	cd .. && docker build --platform linux/amd64 -f narration/Dockerfile -t tta-narration .
