FROM alpine:3.17.5 AS base

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=django_settings

RUN adduser -D -g '' uwsgi

RUN mkdir -p /app/log
RUN chown uwsgi /app/log
VOLUME /app/log

RUN mkdir -p /app/media
RUN chown uwsgi /app/media
VOLUME /app/media

EXPOSE 8000/tcp

RUN apk update && apk add uwsgi uwsgi-python uwsgi-router_static python3 py3-pip py3-wheel py3-psycopg2 py3-pyldap py3-cryptography gdal gettext tzdata

WORKDIR /app/

RUN mkdir castellum
COPY setup.cfg setup.py package.json uwsgi.ini LICENSE COPYRIGHT ./
COPY castellum/__init__.py castellum/

RUN pip3 install -e .[ldap,axes,model-stats]

COPY castellum/ castellum

RUN django-admin compilemessages -l de --settings=castellum.settings.bare


FROM base AS static
RUN apk add npm
RUN npm install --omit=dev
COPY .misc/extract_fullcalendar_css.sh extract_fullcalendar_css.sh
RUN ./extract_fullcalendar_css.sh
RUN django-admin collectstatic --no-input --settings=castellum.settings.bare


FROM base AS final
COPY --from=static /app/static/ static
USER uwsgi
CMD ["uwsgi", "uwsgi.ini"]
