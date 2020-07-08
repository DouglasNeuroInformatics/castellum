FROM node
COPY package.json .
RUN npm install --production

FROM buildpack-deps

ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive
ENV BUILDPKGS gettext python3-pip python3-wheel python3-setuptools
ENV RUNTIMEPKGS uwsgi uwsgi-plugin-python3 python3 python3-psycopg2 python3-ldap libmagic1 gdal-bin busybox-static

RUN adduser --disabled-login --gecos '' uwsgi

RUN mkdir -p /log
RUN chown uwsgi /log
VOLUME /log

RUN mkdir -p /media
RUN chown uwsgi /media
VOLUME /media

RUN apt-get update -q && \
    apt-get install --no-install-recommends -y $BUILDPKGS $RUNTIMEPKGS && \
    rm -rf /var/lib/apt/lists/*

COPY castellum/ code/castellum/
COPY setup.py LICENSE code/
COPY --from=0 node_modules/ code/node_modules/
WORKDIR code/

RUN pip3 install -e . && \
    pip3 install django-auth-ldap django-axes

RUN django-admin collectstatic --no-input --settings=castellum.settings.bare && \
    django-admin compilemessages -l de
