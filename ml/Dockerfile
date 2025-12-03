FROM python:3.12.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN uv sync --locked
EXPOSE 8080


CMD ["uv", "run", "fastapi", "run", "--port", "8080"]
