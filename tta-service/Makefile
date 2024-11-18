# Initialize the virtual environment and install dependencies
install:
	pip install -e .

lint:
	pylint --rcfile=../.pylintrc src

# Run the FastAPI application
run:
	cd ttaservice && \
	uvicorn main:app --reload --port 8000