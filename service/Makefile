install:
	python -m venv .venv
	.venv/bin/pip install -e ../aws -e ../types -e .

run:
	@chmod +x ./run.sh
	@./run.sh

lint:
	.venv/bin/python -m pylint --rcfile=../.pylintrc tta_service
