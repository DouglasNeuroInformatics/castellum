![pipeline status](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/build.svg)
![coverage report](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/coverage.svg)

# Castellum

Castellum is a privacy-compliant subject database for scientific
research.

## Status

This project is still in development. There may be severe vulnerabilities
in the code. It is strongly recommended not to use this in production
yet.

## Development

The following commands will install everything and start a local testserver (on ubuntu):

    sudo apt install python3 npm python3-dev libldap2-dev libsasl2-dev libmagic1 docker-compose gettext
    cd castellum
    python3 -m venv .venv
    make install_githooks
    make  # start castellum

You can login with user "admin" and password "123".

After pulling new changes it is recommended to rebuild the databases and migrations:

    make reset_databases

## Testing

The command `pytest` will execute all tests. (postgres needs to be running)

## Links

-   Project home page: https://www.mpib-berlin.mpg.de/en/research/lifespan-psychology/castellum
-   Source code: https://git.mpib-berlin.mpg.de/castellum/castellum/
-   Code of conduct: https://www.mpg.de/11961177/code-of-conduct-en.pdf
