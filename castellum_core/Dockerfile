FROM alpine
ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gcc musl-dev postgresql-dev openldap-dev cyrus-sasl-dev python3-dev
ENV RUNTIMEPKGS uwsgi uwsgi-python3 python3 nodejs-npm openldap postgresql-libs libressl2.6-libtls

RUN apk update && echo $BUILDPKGS $RUNTIMEPKGS && apk add $BUILDPKGS $RUNTIMEPKGS

COPY ./ code/
WORKDIR code/

RUN echo 'python3 /code/castellum_core/manage.py clear_sessions' > /etc/periodic/daily/castellum_clear_sessions
RUN chmod 755 /etc/periodic/daily/castellum_clear_sessions

RUN pip3 install -e .
RUN npm install

RUN apk del $BUILDPKGS

RUN python3 castellum_core/manage.py collectstatic --no-input
