FROM alpine:3.16.4 AS base

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=django_settings

RUN adduser -D -g '' uwsgi

RUN mkdir -p /code/log
RUN chown uwsgi /code/log
VOLUME /code/log

RUN mkdir -p /code/media
RUN chown uwsgi /code/media
VOLUME /code/media

EXPOSE 8000/tcp

RUN apk update && apk add uwsgi uwsgi-python uwsgi-router_static python3 py3-pip py3-wheel py3-psycopg2 py3-pyldap py3-cryptography gdal gettext

WORKDIR code/

RUN mkdir castellum
COPY setup.cfg setup.py package.json uwsgi.ini LICENSE COPYRIGHT ./
COPY castellum/__init__.py castellum/

RUN pip3 install -e . && \
    pip3 install django-auth-ldap django-axes django-model-stats

COPY castellum/ castellum

RUN django-admin compilemessages -l de --settings=castellum.settings.bare

CMD ["uwsgi", "uwsgi.ini", "--processes", "10", "--cheaper", "1"]


FROM base AS static
RUN apk add npm
RUN npm install --omit=dev
RUN django-admin collectstatic --no-input --settings=castellum.settings.bare


FROM base AS final
COPY --from=static /code/castellum/collected_static castellum/collected_static
