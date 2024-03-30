FROM ubuntu

WORKDIR /opt

RUN apt-get update

RUN apt-get install python3.10 -y

RUN apt-get install python3-pip -y

RUN mkdir source-code

COPY requirements.txt source-code

COPY consummer.py source-code

RUN pip3 install -r /opt/source-code/requirements.txt

CMD ["python3", "source-code/consummer.py"]