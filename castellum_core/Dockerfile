FROM alpine
ENV PYTHONUNBUFFERED 1
ENV BUILDPKGS gcc musl-dev postgresql-dev openldap-dev cyrus-sasl-dev python3-dev
ENV RUNTIMEPKGS uwsgi uwsgi-python3 python3 nodejs-npm openldap postgresql-libs libressl2.6-libtls

RUN apk update && echo $BUILDPKGS $RUNTIMEPKGS && apk add $BUILDPKGS $RUNTIMEPKGS

COPY ./ code/
WORKDIR code/

RUN pip3 install -e .
RUN npm install

RUN apk del $BUILDPKGS
