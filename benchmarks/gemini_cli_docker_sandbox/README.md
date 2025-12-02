# Gemini CLI Docker Sandbox

This directory provides the infrastructure for running benchmarks in a sandboxed Docker environment using the Gemini CLI. It utilizes a **multi-stage build approach** where a common "base" image supports multiple "variant" images with different tool or agent configurations.

## Directory Structure

*   `base/`: The foundation image.
    *   **Dockerfile:** Installs Python 3.11, Node.js 22.x, git, curl, `uv`, and `@google/gemini-cli`.
    *   **Tag:** `gemini-cli-base`

*   `adk-python/`: The standard variant for the Python ADK.
    *   **Dockerfile:** Inherits from `gemini-cli-base`. Clones the `adk-python` repo into `/repos/adk-python`.
    *   **Tag:** `adk-gemini-sandbox:adk-python` (or `:latest`)
    *   **Purpose:** Standard environment for testing agents against the codebase.

*   `gemini-cli-mcp-context7/`: A variant configured with an MCP server.
    *   **Dockerfile:** Inherits from `gemini-cli-base`. Installs `mcp` Python package and configures `settings.json`.
    *   **Tag:** `gemini-cli-mcp-context7`
    *   **Purpose:** Tests the Gemini CLI's ability to use the `context7` MCP server (remote HTTP) to access repository context.

## Usage

### 1. Build the Base Image

You **must** build the base image first.

```bash
docker build -t gemini-cli-base benchmarks/gemini_cli_docker_sandbox/base/
```

### 2. Build a Variant Image

After building the base, you can build any variant.

**Build `adk-python` variant:**
```bash
docker build -t adk-gemini-sandbox:adk-python benchmarks/gemini_cli_docker_sandbox/adk-python/
```

**Build `gemini-cli-mcp-context7` variant:**
```bash
docker build -t gemini-cli-mcp-context7 benchmarks/gemini_cli_docker_sandbox/gemini-cli-mcp-context7/
```

### 3. Running Benchmarks

Update your `GeminiCliDockerAnswerGenerator` configuration to point to the specific variant tag you built.

```python
from benchmarks.answer_generators.gemini_cli_docker_answer_generator import GeminiCliDockerAnswerGenerator

# For standard ADK tests
generator_standard = GeminiCliDockerAnswerGenerator(
    model_name="gemini-2.5-flash",
    image_name="adk-gemini-sandbox:adk-python"
)

# For MCP integration tests
generator_mcp = GeminiCliDockerAnswerGenerator(
    model_name="gemini-2.5-flash",
    image_name="gemini-cli-mcp-context7"
)
```
