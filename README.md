![pipeline status](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/build.svg)
![coverage report](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/coverage.svg)

# Castellum

Castellum is a privacy-compliant subject database for scientific
research.

## Status

This project is still in development. There may be severe vulnerabilities
in the code. It is strongly recommended not to use this in production
yet.

## Usage

Example setup:

    docker-compose -f docker-compose.yml -f docker-compose.manage.yml up

For more details, see `docs/deployment.md`.

## Development

The following commands will install everything and start a local testserver (on ubuntu):

    sudo apt install python3 npm python3-dev libldap2-dev libsasl2-dev
    cd castellum
    python3 -m venv .env
    . .env/bin/activate
    make install-githooks
    make bootstrap
    make run

You can login with user "admin" and password "123".

After pulling new changes it is recommended to rebuild the databases and migrations:

    make reset_databases

## Testing

The command `tox` will execute all tests.

## Links

-   Project home page: https://www.mpib-berlin.mpg.de/en/research/lifespan-psychology/castellum
-   Source code: https://git.mpib-berlin.mpg.de/castellum/castellum/
-   Code of conduct: https://www.mpg.de/11961177/code-of-conduct-en.pdf
