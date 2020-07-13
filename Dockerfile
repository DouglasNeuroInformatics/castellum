FROM node
COPY package.json .
RUN npm install --production

FROM alpine

ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gcc musl-dev postgresql-dev openldap-dev cyrus-sasl-dev python3-dev gettext
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
COPY setup.py LICENSE code/
COPY --from=0 node_modules/ code/node_modules/
WORKDIR code/

RUN pip3 install -U pip && \
    pip3 install -e . && \
    pip3 install django-auth-ldap django-axes

RUN django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de

RUN apk del $BUILDPKGS
