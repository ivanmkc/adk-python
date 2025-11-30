# Base image from the instructions
FROM python:3.11-slim-bookworm

# Switch to root to install packages and Python environment
USER root

# Install git, curl, ca-certificates, gnupg
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22.x (LTS)
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv (https://astral.sh/uv/install.sh)
# Note: Installer now defaults to /root/.local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv

# Install Gemini CLI
RUN npm install -g @google/gemini-cli

# Create node user for compatibility
RUN useradd -m -u 1000 node

# Create repos directory
RUN mkdir -p /repos

# Clone the adk-python repository into /repos/adk-python
RUN git clone https://github.com/google/adk-python.git /repos/adk-python

# Set the working directory to the repo to install dependencies
WORKDIR /repos/adk-python

# Create a virtual environment and install ADK dependencies
RUN uv venv .venv --python 3.11 \
    && . .venv/bin/activate \
    && uv sync --all-extras

# Set the final working directory to /repos
WORKDIR /repos

# Switch back to a non-root user
USER node
