FROM python:3.7

RUN pip install python-telegram-bot==20.0a2 requests beautifulsoup4

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/main.py
