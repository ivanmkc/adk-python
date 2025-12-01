#!/bin/bash

# Substitute environment variables in settings.json
# We explicitly list variables we want to substitute to avoid accidental leaks or malformed JSON if user passes others,
# but for simplicity here we assume CONTEXT7_API_KEY is the main one.
# Note: envsubst with no arguments substitutes ALL environment variables.
envsubst < /root/.gemini/settings.json.template > /root/.gemini/settings.json

# Check for GEMINI_API_KEY or Vertex AI credentials
if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_GENAI_USE_VERTEXAI" ]; then
  echo "Error: GEMINI_API_KEY or GOOGLE_GENAI_USE_VERTEXAI environment variable not set."
  exit 1
fi

# Pass through all arguments to the gemini CLI
exec gemini "$@"
