install:
	cd script && make install
	cd narration && make install

# RunPod, as deploy/runpod.toml says (python3 -m deploy --help for the rest)
plan apply status:
	python3 -m deploy $@

test-deploy:
	script/.venv/bin/python -m pytest -q deploy/tests
	script/.venv/bin/python -m pylint --rcfile=.pylintrc deploy
	script/.venv/bin/python -m mypy deploy
