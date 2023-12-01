FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/parser_app

COPY . .
RUN apt-get update

RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000


