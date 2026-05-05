# Stage 1 -- builder
FROM python:3.14-alpine AS builder

WORKDIR /app

# Alpine needs these build tools for some Python packages
RUN apk add --no-cache gcc musl-dev libffi-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2 -- runtime
FROM python:3.14-alpine AS runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# Alpine uses addgroup/adduser differently from Debian
RUN addgroup -S lexio && \
    adduser -S -G lexio lexio

RUN chown -R lexio:lexio /app

USER lexio

EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]