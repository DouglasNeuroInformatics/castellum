FROM alpine:3.23.7 AS base

ENV PIP_BREAK_SYSTEM_PACKAGES 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/
ENV DJANGO_SETTINGS_MODULE=django_settings

RUN adduser -D -g '' user

RUN mkdir -p /app/log && chown user /app/log
VOLUME /app/log

RUN mkdir -p /app/media && chown user /app/media
VOLUME /app/media

EXPOSE 8000/tcp

RUN apk update && apk add \
    uwsgi \
    uwsgi-python \
    uwsgi-router_static \
    python3 \
    py3-gunicorn \
    py3-pip \
    py3-wheel \
    py3-psycopg-c \
    py3-pyldap \
    py3-cryptography \
    libspatialite-dev \
    gdal \
    gettext \
    tzdata

WORKDIR /app/

RUN mkdir castellum
COPY pyproject.toml uwsgi.ini LICENSE COPYRIGHT ./
COPY castellum/__init__.py castellum/

RUN pip3 install -e .[ldap,axes,model-stats,storage-timestamps] && pip cache purge

COPY castellum/ castellum

RUN python3 -m django compilemessages -l de --settings=castellum.settings.bare


FROM docker.io/library/node:latest AS node
COPY package.json ./
RUN npm install --omit=dev


FROM base AS static
COPY --from=node node_modules node_modules
RUN python3 -m django collectstatic --no-input --settings=castellum.settings.bare


FROM base AS final
COPY --from=static /app/static/ static
USER user
CMD ["uwsgi", "uwsgi.ini"]
