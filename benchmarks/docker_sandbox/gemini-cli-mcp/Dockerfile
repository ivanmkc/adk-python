FROM gemini-cli-base

# Set working directory
# WORKDIR /app # Base image already sets /app

# Install the mcp[cli] package needed for the context7 server
RUN pip install "mcp[cli]"

# Create the .gemini directory and copy the settings.json file
RUN mkdir -p /root/.gemini/
COPY settings.json /root/.gemini/settings.json

# Create an entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
