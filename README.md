# Text-To-Audiobook

TTA (Text-to-Audiobook) transforms book text into a multi-speaker audiobook experience.

### Installation and Setup

1. **Install Make**: Make is a build automation tool that is required to setup the project. You can install Make on your system by following the instructions for your operating system:
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install build-essential`
   - **Fedora/CentOS/RHEL**: `sudo dnf install make`
   - **macOS (with Homebrew)**: `brew install make`
   - **Windows**: Install MinGW or Cygwin, which include Make.
2. **Clone the repository**: Clone the project repository to your local machine using Git:
   - `git clone https://github.com/FayZ676/audiobook-generator.git`
3. **Navigate to the project directory**: Change into the project directory:
   - `cd audiobook-generator`
4. **Run `make init`**: This command will setup the virtual environment and install the project dependencies:
   - `make init`

This will create a virtual environment named `venv` in your project directory, activate it, and install the project dependencies. You can then use the virtual environment to run the project.

**Note**: Make sure you have Python 3.10 or later installed on your system, as specified in the project's `pyproject.toml` file.
