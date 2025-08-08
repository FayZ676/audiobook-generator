install:
	python -m venv .venv
	(source .venv/bin/activate || . .venv/bin/activate) && \
	pip install -e ../aws -e ../types -e .

run:
	@chmod +x ./run.sh
	@./run.sh

lint:
	(source .venv/bin/activate || . .venv/bin/activate) && \
	pylint --rcfile=../.pylintrc tta_service
