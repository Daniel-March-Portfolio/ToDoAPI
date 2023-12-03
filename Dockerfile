FROM python:3.12

COPY requirements/common.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY src src
COPY main.py main.py

ENTRYPOINT python3 main.py