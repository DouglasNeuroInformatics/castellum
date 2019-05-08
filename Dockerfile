FROM alpine

ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gcc musl-dev postgresql-dev openldap-dev cyrus-sasl-dev python3-dev gettext
ENV RUNTIMEPKGS uwsgi uwsgi-python3 python3 nodejs-npm openldap postgresql-libs libressl

RUN adduser -D -g '' uwsgi
RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log
VOLUME /media

RUN apk update && echo $BUILDPKGS $RUNTIMEPKGS && apk add $BUILDPKGS $RUNTIMEPKGS

COPY castellum/ code/castellum/
COPY setup.py package.json LICENSE code/
WORKDIR code/

RUN pip3 install -U pip && \
    pip3 install -e . && \
    npm install

RUN django-admin makemigrations --settings=castellum.settings.bare && \
    django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de

RUN apk del $BUILDPKGS
