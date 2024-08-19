ARG PYTHON_VERSION=3.10.13
FROM python:${PYTHON_VERSION}-slim AS base

RUN apt-get update && \
    apt-get install -y pipenv && \
    apt-get install -y \
    fontconfig \
    fonts-dejavu \
    fonts-dejavu-core \
    fonts-dejavu-extra \
    fonts-liberation \
    fonts-noto \
    fonts-ubuntu &&\ 
    rm -rf /var/lib/apt/lists/*

ENV PORT=7860

ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /app

COPY requirements.txt .

RUN pipenv install --dev --ignore-pipfile

COPY . .

EXPOSE 7860

RUN python -V

CMD pipenv run python -m gunicorn main:app -b 0.0.0.0:7860 -w 8 --timeout 600