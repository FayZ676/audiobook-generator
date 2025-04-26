# Text-To-Audiobook

TTA (Text-to-Audiobook) transforms book text into a multi-speaker audiobook experience.

## Installation and Setup

**Note**: Make sure you have Python 3.12 or later installed on your system.

1. **Install Make**: Make is a build automation tool that is required to setup the project. You can install Make on your system by following the instructions for your operating system:
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install build-essential`
   - **Fedora/CentOS/RHEL**: `sudo dnf install make`
   - **macOS (with Homebrew)**: `brew install make`
   - **Windows**: Install MinGW or Cygwin, which include Make.
2. **Install FFMPEG**: This package is needed in order to work with the narration audio files.
3. **Clone the repository**: Clone the project repository to your local machine using Git:
   - `git clone https://github.com/FayZ676/audiobook-generator.git`
4. **Navigate to the project directory**: Change into the project directory:
   - `cd audiobook-generator`
5. **Run **`**make setup**` : This command will setup the virtual environment, install the project dependencies, and setup some git hooks:
   - `make setup`

## Testing

- Run `make test_all` from the project's root directory to lint and run all tests.
- A pre-push .git hook is configured when you run the `make setup` command that will automatically run the all the tests before pushing. If for some reason you don't have the .git hook set up, you can always run `make setup_git_hook` to automatically create the .git hooks.

## Deployment

![Deployment Event Sequence](/.eraser/o9mImca0SEbPEjiR7g0l___tYElYs9QXdYxRBDRRTDqqgBgTaT2___---figure---urHTwqXj1OgC2s8P6kuKo---figure---BJTOFFvJDzsTVIBVg8ITJw.png "Deployment Event Sequence")
