FROM python:3.9.9-slim-buster

LABEL author='rusich' version=1

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src /code

WORKDIR /code

CMD python main.py