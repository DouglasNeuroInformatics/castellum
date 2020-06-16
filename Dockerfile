FROM alpine

ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gcc musl-dev postgresql-dev openldap-dev cyrus-sasl-dev python3-dev gettext nodejs-npm
ENV RUNTIMEPKGS uwsgi uwsgi-python python3 py3-pip openldap postgresql-libs libressl libmagic proj gdal

RUN adduser -D -g '' uwsgi

RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log

RUN mkdir -p /media
RUN chown uwsgi /media
VOLUME /media

RUN apk update && echo $BUILDPKGS $RUNTIMEPKGS && apk add $BUILDPKGS $RUNTIMEPKGS

COPY castellum/ code/castellum/
COPY setup.py package.json LICENSE code/
WORKDIR code/

RUN pip3 install -U pip && \
    pip3 install -e . && \
    pip3 install django-auth-ldap django-axes && \
    npm install --production

RUN django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de

RUN apk del $BUILDPKGS
