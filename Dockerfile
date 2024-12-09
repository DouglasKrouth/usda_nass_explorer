FROM python:3.12.6-slim

ARG POETRY_VERSION=1.8
RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root

ENTRYPOINT ["bash"]

RUN echo "rat"
