FROM python:3.5

RUN mkdir /opt/app
WORKDIR /opt/app
ADD requirements.txt /opt/app
RUN pip install -r requirements.txt

ADD . /opt/app

VOLUME /var/run/docker.sock

CMD ["./runner.py"]
