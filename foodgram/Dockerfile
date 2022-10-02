#!/bin/bash
FROM python:3.7

RUN mkdir /backend

RUN mkdir /app

COPY requirements.txt /app

COPY foodgram/. /app

COPY backend/. /backend

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
