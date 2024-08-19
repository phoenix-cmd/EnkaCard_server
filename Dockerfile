ARG PYTHON_VERSION=3.10.13
FROM python:${PYTHON_VERSION}-slim AS base

RUN apt-get update && apt-get install -y && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

ENV PORT=7860

WORKDIR /app

RUN python -m pip install -r requirements.txt

COPY . .

EXPOSE 7860

CMD python3 -m gunicorn main:app -b 0.0.0.0:7860 -w 8 --timeout 600