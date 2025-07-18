# Text-To-Audiobook

## Project overview

There are 4 key services that make up the project.

1. **`/speech`:** Custom text to speech generator.
2. **`/script`:** Converts text into JSON format needed for speech generation.
3. **`/service`:** Recieves requests from `client` and orchestrates `speech` and `script` processes in order to generate audiobook segments.
4. **`/client`:** User interface for interacting with the audiobook generator.

## Installation and Setup

> ‼️ **Make sure you have Python 3.12 and Node.js installed on your system.**

#### (Option 1/2) Quick Setup

**Run `make setup` in root**: This command will setup the virtual environments and install dependencies for all 4 services.

#### (Option 2/2) Manual Service Installation

Alternatively, you can install the services individually by running the `make install` command in their respective directories.

### Environment Variables

Each service has a `.env.example` file with all the environment variables required.

1. Copy the `.env.example` file and rename the duplicate to `.env.local`.
2. Populate `.env.local` with your keys.

### Running Locally

To run the application locally run the `make run` command in a separate terminal for each service.

> ‼️ **When running services locally, you need to add `/runsync` to the endpoint URLs for the `script` and `speech` services. This is required to enable synchronous communication. Refer to the service router files (`service/tta_service/routers/script.py` and `service/tta_service/routers/narration.py`).**
