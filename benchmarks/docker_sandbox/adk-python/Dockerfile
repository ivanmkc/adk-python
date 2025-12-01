# Inherit from the local base image
# Build with: docker build -t adk-gemini-sandbox:base -f benchmarks/docker_sandbox/base/Dockerfile .
FROM adk-gemini-sandbox:base

# Create repos directory
RUN mkdir -p /repos

# Clone the adk-python repository into /repos/adk-python
RUN git clone https://github.com/google/adk-python.git /repos/adk-python

# Set the final working directory to /repos
WORKDIR /repos

# Switch back to a non-root user
USER node
