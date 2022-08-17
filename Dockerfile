FROM node
COPY package.json .
RUN npm install --omit=dev

FROM alpine:3.16.2

ENV PYTHONUNBUFFERED 1

RUN adduser -D -g '' uwsgi

RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log

RUN mkdir -p /media
RUN chown uwsgi /media
VOLUME /media

RUN apk update && apk add uwsgi uwsgi-python uwsgi-router_static python3 py3-pip py3-wheel py3-psycopg2 py3-pyldap py3-cryptography libmagic gdal gettext

WORKDIR code/

RUN mkdir castellum
COPY setup.cfg setup.py LICENSE ./
COPY castellum/__init__.py castellum/
COPY --from=0 node_modules/ node_modules

RUN pip3 install -e . && \
    pip3 install django-auth-ldap django-axes django-model-stats

COPY castellum/ castellum

RUN django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de
