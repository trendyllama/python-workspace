
FROM docker.io/python:alpine

RUN apk update && apk add bash uv git nodejs npm ripgrep openssh-client github-cli

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
