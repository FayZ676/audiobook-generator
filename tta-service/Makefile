# Initialize the virtual environment and install dependencies
init:
    pip install -e .

lint:
	pylint --rcfile=../.pylintrc src

# Run the FastAPI application
run:
    uvicorn main:app --reload --port 8000
