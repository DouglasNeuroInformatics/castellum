FROM python:3.6-alpine3.7
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add gcc make uwsgi uwsgi-python3 nodejs-npm python-dev musl-dev postgresql-dev openldap openldap-dev cyrus-sasl-dev

COPY ./ code/
WORKDIR code/

RUN make install
