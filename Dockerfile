FROM node:14.16.0
COPY package.json .
RUN npm install --production

FROM alpine:3.13.3

ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gettext py3-pip py3-wheel
ENV RUNTIMEPKGS uwsgi uwsgi-python python3 py3-psycopg2 py3-pyldap libmagic proj gdal

RUN adduser -D -g '' uwsgi

RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log

RUN mkdir -p /media
RUN chown uwsgi /media
VOLUME /media

RUN apk update && echo $BUILDPKGS $RUNTIMEPKGS && apk add $BUILDPKGS $RUNTIMEPKGS

WORKDIR code/

COPY setup.cfg setup.py LICENSE ./
COPY --from=0 node_modules/ node_modules

RUN pip3 install -e . && \
    pip3 install django-auth-ldap django-axes

COPY castellum/ castellum

RUN django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de
