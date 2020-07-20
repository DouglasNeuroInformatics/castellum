# Castellum

Castellum is a privacy-compliant subject database for scientific
research.

## Status

This project is still in development. There may be severe vulnerabilities
in the code. It is strongly recommended not to use this in production
yet.

## Development

The following commands will install everything and start a local testserver (on ubuntu):

    sudo apt install python3-venv npm make docker-compose gettext gdal-bin
    cd castellum
    make install_githooks
    make  # start castellum

You can login with user "admin" and password "123".

## Testing

The command `pytest` will execute all tests.

## Links

-   Project home page: https://www.mpib-berlin.mpg.de/research-data/castellum
-   Source code: https://git.mpib-berlin.mpg.de/castellum/castellum/
-   Documentation: https://castellum.mpib.berlin/documentation/en/
-   Code of conduct: https://www.mpg.de/11961177/code-of-conduct-en.pdf
