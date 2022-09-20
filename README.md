# Castellum

Castellum is a subject database system developed at the Max Planck
Society. Its main goals are:

-   GDPR compliant data protection and security
-   Flexibility so it can be used in different organisations

## Features

-   **Subject management**: Castellum is a central place to collect
    references to all data related to a subject, e.g. so it can be
    deleted on request.
-   **Pseudonym service**: Contact details are stored in Castellum so
    all other databases can work with pseudonyms instead.
-   **Recruitment**: Castellum allows you to find potential participants
    from an existing pool using study specific filters.
-   **Appointments**: You can manage appointments for test sessions.

## Quickstart

First install some system packages. The exact command depends on your
operating system. This is an example for Ubuntu:

    sudo apt install python3-pip python3-venv npm make gettext sqlite3 gdal-bin libsqlite3-mod-spatialite

After that, running `make` inside the project folder will install all
dependencies and start a test server. You can then log in with username
"admin" and password "password".

For more detailled instructions, see the [developer
documentation](https://git.mpib-berlin.mpg.de/castellum/castellum/-/tree/main/docs).

## Links

-   Contact: castellum@mpib-berlin.mpg.de
-   Source code: https://git.mpib-berlin.mpg.de/castellum/castellum/
-   Releases: https://git.mpib-berlin.mpg.de/castellum/castellum/-/releases
    ([feed](https://git.mpib-berlin.mpg.de/castellum/castellum/-/tags?format=atom))
-   End-user documentation: https://castellum.mpib.berlin/documentation/en/
-   Code of conduct: https://www.mpg.de/11961177/code-of-conduct-en.pdf
