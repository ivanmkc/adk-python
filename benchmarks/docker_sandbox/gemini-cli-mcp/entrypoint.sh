#!/bin/bash

# Ensure Gemini CLI uses the custom config
# No longer needed as settings.json is in default location
# export GEMINI_CONFIG="/root/.config/gemini_config.json"

# Check for GEMINI_API_KEY or Vertex AI credentials
if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_GENAI_USE_VERTEXAI" ]; then
  echo "Error: GEMINI_API_KEY or GOOGLE_GENAI_USE_VERTEXAI environment variable not set."
  exit 1
fi

# Pass through all arguments to the gemini CLI
exec gemini "$@"
