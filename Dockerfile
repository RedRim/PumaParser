FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/parser_app

COPY . .
RUN apt-get update && \
    apt-get install -y postgresql-client

RUN pip install --no-cache-dir -r requirements.txt

COPY puma_data.json /usr/src/parser_app/your_app/fixtures/puma_data.json

EXPOSE 8000
CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py loaddata puma_data.json && \
    python manage.py runserver 0.0.0.0:8000

