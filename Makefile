init:
	python -m venv .venv
	source .venv/bin/activate && \
	cd generator && make install && \
	cd ../service && make install && \
	python -m spacy download en_core_web_trf

lint_all:
	pylint --rcfile=.pylintrc src

test_all:
	cd tta && make test

setup_git_hook:
	echo '#!/bin/sh\nmake test_all' > .git/hooks/pre-push
	chmod +x .git/hooks/pre-push
	@echo "Pre-push hook has been set up successfully."

setup:
	make init
	make setup_git_hook

aws_stack_create:
	aws cloudformation create-stack --stack-name audiobook-generator --template-body file://cloudformation.yaml --capabilities CAPABILITY_NAMED_IAM

aws_stack_delete:
	aws cloudformation delete-stack --stack-name audiobook-generator

aws_stack_update:
	aws cloudformation update-stack --stack-name audiobook-generator --template-body file://cloudformation.yaml --capabilities CAPABILITY_NAMED_IAM

docker_build:
	docker build --platform linux/amd64 -t audiobook_generator -f generator/Dockerfile .

docker_run:
	docker run --platform linux/amd64 --env-file .env audiobook_generator
