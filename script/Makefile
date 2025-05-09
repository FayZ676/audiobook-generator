install:
	pip install -e ../types -e ../aws -e .

run:
	python tta_script/rp_handler.py --rp_serve_api --rp_api_port 8001

lint:
	pylint --rcfile=../.pylintrc tta_script tests

test:
	pytest --cov=tta --cov-report=term-missing --cov-fail-under=80 tests

docker_build:
	docker build --platform linux/amd64 -t script_generator -f Dockerfile ..

docker_run:
	docker run -it -p 8001:8000 --platform linux/amd64 --env-file ../.env script_generator
