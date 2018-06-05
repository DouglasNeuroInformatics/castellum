![pipeline status](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/build.svg)
![coverage report](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/coverage.svg)

# Castellum

Castellum is a privacy-compliant recruiting database for scientific contexts.

## Usage

Example setup:

    docker-compose -f docker-compose.yml -f docker-compose.manage.yml up

For more details, see `docs/deployment.md`.

## Development

The following commands will install everything and start a local testserver (on ubuntu):

    sudo apt install python3 npm python3-dev libldap2-dev libsasl2-dev
    python3 -m venv .env
    . .env/bin/activate
    cd castellum_core
    make bootstrap
    make run

You can login with user "admin" and password "123".
