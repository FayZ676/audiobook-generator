<p><a target="_blank" href="https://app.eraser.io/workspace/o9mImca0SEbPEjiR7g0l" id="edit-in-eraser-github-link"><img alt="Edit in Eraser" src="https://firebasestorage.googleapis.com/v0/b/second-petal-295822.appspot.com/o/images%2Fgithub%2FOpen%20in%20Eraser.svg?alt=media&amp;token=968381c8-a7e7-472a-8ed6-4a6626da5501"></a></p>

# Text-To-Audiobook

TTA (Text-to-Audiobook) transforms book text into a multi-speaker audiobook experience.

## Installation and Setup

**Note**: Make sure you have Python 3.12 or later and Node.js installed on your system.

### Prerequisites

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

### Quick Setup

**Run `make setup`**: This command will setup the virtual environment, install all service dependencies, and setup git hooks:
```bash
make setup
```

### Manual Service Installation

Alternatively, you can install each service individually:

1. **Script Service**: 
   ```bash
   cd script
   make install
   cd ..
   ```

2. **Speech Service**:
   ```bash
   cd speech
   make install
   cd ..
   ```

3. **API Service**:
   ```bash
   cd service
   make install
   cd ..
   ```

4. **Client Application**:
   ```bash
   cd client
   npm install
   cd ..
   ```

### Environment Variables

Each service requires environment variables to be configured. Copy the example files and update them with your values:

- **Script Service**: Copy `script/.env.example` to `script/.env` and configure:
  - AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
  - OpenAI API key (OPENAI_API_KEY)
  - S3 bucket names (SCRIPT_RESULTS_BUCKET, VOICES_BUCKET)

- **Speech Service**: Copy `speech/.env.example` to `speech/.env` and configure:
  - AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
  - S3 bucket names (VOICES_AUDIOS_BUCKET, SPEECH_RESULTS_BUCKET, MODEL_FILES_BUCKET)

- **API Service**: Copy `service/.env.example` to `service/.env` and configure:
  - AWS credentials and S3 buckets
  - Pusher configuration (PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET, PUSHER_CLUSTER)
  - Service URLs and API keys (SERVICE_API_URL, SPEECH_API_URL, SCRIPT_API_URL)

- **Client**: Copy `client/.env.example` to `client/.env.local` and configure:
  - Service URL (AUDIOBOOK_SERVICE_URL)
  - Pusher configuration (NEXT_PUBLIC_PUSHER_APP_KEY, NEXT_PUBLIC_PUSHER_CLUSTER)
  - Clerk authentication keys (NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY)

### Running Locally

To run the application locally, you need to start each service in separate terminals:

1. **Script Service**:
   ```bash
   cd script
   make run
   ```
   Runs on http://127.0.0.1:8001

2. **Speech Service**:
   ```bash
   cd speech
   make run
   ```
   Runs on http://127.0.0.1:8002

3. **API Service**:
   ```bash
   cd service
   make run
   ```
   Runs on http://127.0.0.1:8000

4. **Client Application**:
   ```bash
   cd client
   npm run dev
   ```
   Runs on http://localhost:3000

#### Important Note for Local Development

When running services locally, you need to add `/runsync` to the endpoint URLs for the script and speech services to enable synchronous communication. This is mentioned in the service router files (`service/tta_service/routers/script.py` and `service/tta_service/routers/narration.py`) and is vital for proper local communication between services.

## Testing

- Run `make test_all` from the project's root directory to lint and run all tests.
- A pre-push .git hook is configured when you run the `make setup` command that will automatically run the all the tests before pushing. If for some reason you don't have the .git hook set up, you can always run `make setup_git_hook` to automatically create the .git hooks.
