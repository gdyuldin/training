FROM python:3.5

RUN mkdir /opt/app
WORKDIR /opt/app
ADD . /opt/app
RUN pip install .

VOLUME /var/run/docker.sock

EXPOSE 8000

CMD ["python",  "-m",  "training_backend.run"]
