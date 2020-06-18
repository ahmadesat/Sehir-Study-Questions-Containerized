FROM python:3.8-alpine

WORKDIR /opt/sehirstudyquestions
ADD . /opt/sehirstudyquestions

RUN pip3 install -r requirements.txt



ADD dump.sql /docker-entrypoint-initdb.d
ENTRYPOINT FLASK_APP=/opt/sehirstudyquestions/main.py flask run --host=0.0.0.0
