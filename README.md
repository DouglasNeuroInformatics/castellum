![coverage report](https://git.mpib-berlin.mpg.de/castellum/castellum/badges/master/coverage.svg)]

# Castellum

Castellum is a privacy-compliant recruiting database for scientific contexts.

## Installation

If python3 is available on your system, the following commands will install everything and start a
local testserver:

    python3 -m venv .env
    . .env/bin/activate
    cd castellum_core
    make bootstrap
    make run

You can login with user "admin" and password "123".
