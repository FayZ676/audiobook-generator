init:
	cd script && make install && \
	cd ../speech && make install && \
	cd ../service && make install && \
	cd ../client && make install

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

aws_stack_describe:
	aws cloudformation describe-stacks --stack-name audiobook-generator

clerk_invite:
	curl https://api.clerk.com/v1/invitations -X POST \
	-d '{"email_address": "$(CLERK_EMAIL)", "redirect_url": "$(CLERK_REDIRECT_URL)", "ignore_existing": true, "expires_in_days": 30}' \
	-H "Authorization:Bearer $(CLERK_API_KEY)" \
	-H 'Content-Type:application/json'
