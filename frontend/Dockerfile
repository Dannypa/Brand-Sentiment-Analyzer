FROM python:3.12.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN uv sync --locked
EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "main.py","--server.port=8501", "--server.address=0.0.0.0"]
