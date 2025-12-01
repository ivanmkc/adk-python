FROM gemini-cli-base

# Install gettext-base for envsubst
RUN apt-get update && apt-get install -y --no-install-recommends gettext-base && rm -rf /var/lib/apt/lists/*

# Set working directory
# WORKDIR /app # Base image already sets /app

# Create the .gemini directory and copy the settings.json template
RUN mkdir -p /root/.gemini/
COPY settings.json /root/.gemini/settings.json.template

# Copy an entrypoint script that performs env var substitution
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
