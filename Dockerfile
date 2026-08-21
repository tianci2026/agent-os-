FROM python:3.9-slim

WORKDIR /app

COPY agent_os/ ./agent_os/
COPY serve_ui.py .
COPY frontend/ ./frontend/
COPY pyproject.toml .

EXPOSE 8787

ENV AGENT_OS_STORE_DIR=/data
ENV AGENT_OS_AUTH=1

VOLUME ["/data"]

CMD ["python", "serve_ui.py", "/data", "8787", "0.0.0.0"]
