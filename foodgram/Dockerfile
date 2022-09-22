FROM python:3.7

RUN mkdir /backend

RUN mkdir /app

COPY ../requirements.txt /app

COPY foodgram/. /app

COPY ../backend/. /backend

WORKDIR /app

RUN pip3 install -r requirements.txt --no-cache-dir

CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
