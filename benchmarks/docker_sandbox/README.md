# ADK Docker Sandbox

This directory provides the infrastructure for running benchmarks in a sandboxed Docker environment using the Gemini CLI. This ensures a consistent and isolated environment for evaluating agent performance, particularly for tasks involving file system inspection and command execution.

## Overview

The sandbox environment is built as a Docker image that mimics a typical developer setup. It includes:
*   **Python 3.11**: The core runtime.
*   **Node.js 22.x & npm**: Required for the Gemini CLI.
*   **Gemini CLI**: The `@google/gemini-cli` package installed globally.
*   **ADK Python Source Code**: Cloned into `/repos/adk-python` to provide context for the agent.
*   **Standard Tools**: `git`, `curl`, `uv` (for fast Python dependency management).

## Directory Structure

*   `Dockerfile`: Defines the image build process.
    *   Base image: `python:3.11-slim-bookworm`
    *   Installs dependencies (Node.js, git, etc.)
    *   Clones `adk-python` into `/repos/adk-python`
    *   Sets up the environment but does *not* set `PYTHONPATH` for execution, treating the code primarily as a reference for the agent.
*   `cloudbuild.yaml`: (Optional) Configuration for building the image using Google Cloud Build.

## Usage

### 1. Building the Image

You can build the image locally or via Cloud Build.

**Local Build:**
```bash
docker build -t adk-gemini-sandbox:latest -f benchmarks/docker_sandbox/Dockerfile .
```

**Cloud Build:**
```bash
gcloud builds submit . --config benchmarks/docker_sandbox/cloudbuild.yaml --project YOUR_PROJECT_ID
```

### 2. Running Benchmarks with Docker

The `GeminiCliDockerAnswerGenerator` class utilizes this image. To use it in benchmarks:

1.  Ensure the image `adk-gemini-sandbox:latest` (or your custom tag) is available locally.
2.  Configure the answer generator in your benchmark script:

```python
from benchmarks.answer_generators.gemini_cli_docker_answer_generator import GeminiCliDockerAnswerGenerator

generator = GeminiCliDockerAnswerGenerator(
    model_name="gemini-2.5-flash",
    image_name="adk-gemini-sandbox:latest"
)
```

The generator automatically prepends a context prompt instructing the agent that it is running inside the container at `/repos` and should look into `./adk-python` for source code.

## troubleshooting

*   **Gemini CLI Errors**: Ensure `GEMINI_API_KEY` or Vertex AI credentials are correctly passed to the environment. The `GeminiCliDockerAnswerGenerator` handles this automatically for standard environment variables.
*   **Platform Warnings**: If running on Apple Silicon (ARM64) and using an AMD64 image, Docker will warn about platform mismatch. This is usually harmless for simple CLI tasks but ideally, build the image for your architecture or use `--platform linux/amd64`.
