FROM python:3.10-alpine AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install poetry && \
    poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root


FROM python:3.10-alpine

WORKDIR /app

COPY --from=builder /app/.venv .venv/
COPY . .

EXPOSE 5000

CMD ["/app/.venv/bin/flask", "run", "--host=0.0.0.0", "--port=5000"]
