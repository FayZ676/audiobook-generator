install:
	@echo "Installing dependencies..."
	@echo "Run: pip install -e ../types && pip install -r requirements.txt"
	@echo "Note: HF_TOKEN environment variable required for Dia TTS"
	@echo "Mac users: torch.compile is automatically disabled for compatibility"

run:
	@echo "Dia TTS POC Example"
	@echo "==================="
	@echo "To run the example, ensure dependencies are installed first:"
	@echo "  make install"
	@echo "  pip install pydantic  # Required by tta_types"
	@echo ""
	@echo "Then run:"
	@echo "  PYTHONPATH=../types:\$$PYTHONPATH python example_usage.py"
	@echo "  PYTHONPATH=../types:\$$PYTHONPATH python test_dia_poc.py"
	@echo ""
	@echo "Mac users: The code automatically handles Mac compatibility"