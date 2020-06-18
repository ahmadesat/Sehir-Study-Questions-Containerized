FROM python:3.8

RUN apt-get update
RUN apt-get install -y python3-pip

RUN pip3 install flask
WORKDIR /opt/sehirstudyquestions
ADD . /opt/sehirstudyquestions


RUN pip3 install -r requirements.txt




ENTRYPOINT FLASK_APP=/opt/sehirstudyquestions/main.py flask run --host=0.0.0.0
