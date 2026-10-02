
FROM docker.io/python:alpine

RUN apk update && apk add uv git nodejs npm ripgrep

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN uv sync --locked && uv build
