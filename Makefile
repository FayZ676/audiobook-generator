init:
	python -m venv venv
	source venv/bin/activate && \
	cd tta && make install && \
	cd ../tta-service && make install && \
	python -m spacy download en_core_web_trf


# Runs linting on the entire application
lint_all:
	pylint --rcfile=.pylintrc src

test_all:
	cd tta && make test

# Sets up a pre-push Git hook that runs the test_all command
setup_git_hook:
	echo '#!/bin/sh\nmake test_all' > .git/hooks/pre-push
	chmod +x .git/hooks/pre-push
	@echo "Pre-push hook has been set up successfully."

setup:
	make init
	make setup_git_hook