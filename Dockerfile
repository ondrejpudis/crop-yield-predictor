FROM python:3.7-slim-stretch

WORKDIR /app

ENV PACKAGE_VERSION=1.0

RUN pip install --upgrade pip && \
    apt-get update && \
    apt-get -y install openssl libssl-dev gcc

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN pip install -e .
