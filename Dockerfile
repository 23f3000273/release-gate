# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt


FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app.py .

RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser

USER appuser

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
