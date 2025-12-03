FROM python:3.12.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD . /app
WORKDIR /app

RUN uv sync --locked
EXPOSE 8080

# RUN useradd app
# USER app

CMD ["uv", "run", "fastapi", "run", "src/api.py", "--port", "8080"]
