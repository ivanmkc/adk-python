# ADK Docker Sandbox

This directory provides the infrastructure for running benchmarks in a sandboxed Docker environment using the Gemini CLI. It uses a **multi-stage build approach** where a common "base" image supports multiple "variant" images with different tool or agent configurations.

## Directory Structure

*   `base/`: The foundation image.
    *   `Dockerfile`: Installs Python 3.11, Node.js 22.x, git, curl, uv, and `@google/gemini-cli`.
*   `adk-python/`: The default variant for the Python ADK.
    *   `Dockerfile`: Clones the `adk-python` repo and sets up dependencies.
*   `[variant_name]/`: Future variants.

## Usage

### 1. Build the Base Image

You **must** build the base image first, tagging it as `adk-gemini-sandbox:base`.

```bash
docker build -t adk-gemini-sandbox:base -f benchmarks/docker_sandbox/base/Dockerfile .
```

### 2. Build a Variant Image

After building the base, you can build any variant. For example, the `adk-python` variant:

```bash
docker build -t adk-gemini-sandbox:adk-python -f benchmarks/docker_sandbox/adk-python/Dockerfile .
```

### 3. Running Benchmarks

Update your `GeminiCliDockerAnswerGenerator` configuration to point to the specific variant tag you built.

```python
from benchmarks.answer_generators.gemini_cli_docker_answer_generator import GeminiCliDockerAnswerGenerator

generator = GeminiCliDockerAnswerGenerator(
    model_name="gemini-2.5-flash",
    image_name="adk-gemini-sandbox:adk-python" # Use the variant tag here
)
```

## Troubleshooting

*   **Platform Warnings**: If running on Apple Silicon (ARM64) and using an AMD64 image, use `--platform linux/amd64` for compatibility if needed.