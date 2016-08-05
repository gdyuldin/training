FROM python:3.5

RUN pip install pytest coverage

RUN mkdir /opt/sandbox

ADD run.sh /opt/sandbox
WORKDIR /opt/sandbox

CMD ["./run.sh"]
