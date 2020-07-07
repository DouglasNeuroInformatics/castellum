FROM node
COPY package.json .
RUN npm install --production

FROM ubuntu

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
ENV BUILDPKGS gcc python3-pip libldap2-dev libsasl2-dev libssl-dev python3-dev gettext
ENV RUNTIMEPKGS uwsgi uwsgi-plugin-python3 python3 libmagic1 gdal-bin

RUN adduser --disabled-login --gecos '' uwsgi

RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log

RUN mkdir -p /media
RUN chown uwsgi /media
VOLUME /media

RUN apt-get update -q && apt-get install -y $BUILDPKGS $RUNTIMEPKGS

COPY castellum/ code/castellum/
COPY setup.py LICENSE code/
COPY --from=0 node_modules/ code/node_modules/
WORKDIR code/

RUN pip3 install -U pip && \
    pip3 install -e . && \
    pip3 install django-auth-ldap django-axes

RUN django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de

RUN apt-get remove -y $BUILDPKGS && apt-get autoremove -y
