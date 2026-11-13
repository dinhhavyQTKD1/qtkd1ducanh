# Dockerfile for Nam Việt Software AI Agent
FROM python:3.12-slim

WORKDIR /app

# Copy project files
COPY . /app

# Zero external dependencies required (Pure Python Standard Library)
# Expose port for localhost / cloud hosting
EXPOSE 8000

# Default command: launch interactive web dashboard server
CMD ["python", "server.py"]

