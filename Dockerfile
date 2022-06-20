FROM node
COPY package.json .
RUN npm install --production

FROM alpine:3.14.6

ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gettext py3-pip py3-wheel
ENV RUNTIMEPKGS uwsgi uwsgi-python uwsgi-router_static python3 py3-psycopg2 py3-pyldap py3-cryptography libmagic proj gdal

RUN adduser -D -g '' uwsgi

RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log

RUN mkdir -p /media
RUN chown uwsgi /media
VOLUME /media

RUN apk update && echo $BUILDPKGS $RUNTIMEPKGS && apk add $BUILDPKGS $RUNTIMEPKGS

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
