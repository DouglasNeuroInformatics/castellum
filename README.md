# Castellum

The General Data Protection Regulation (GDPR) requires organizations to
keep a detailed inventory of the data they collect from individuals.
This can be tricky for research institutes, where researchers often
organize their work with a high degree of autonomy.

Castellum addresses this by acting as a centralized repository where
researchers share information about the individuals from whom they’ve
collected data. It also tracks recruitment consent, helping you to build
a valuable pool of participants for future research projects.

## Features

-   **GDPR Compliance**: Castellum is a central place where researchers
    share details about the individuals they’ve collected data from,
    making it easy to handle requests for access or erasure.
-   **Pseudonym service**: Contact details are stored in Castellum so
    research data can be stored with pseudonyms instead.
-   **Recruitment**: Find potential participants from an existing pool
    using study specific filters.
-   **Appointments**: Manage appointments for test sessions or let
    participants pick themselves.

## Quickstart

First install some system packages. The exact command depends on your
operating system. This is an example for Ubuntu:

    sudo apt install python3-pip python3-venv npm make gettext sqlite3 gdal-bin libsqlite3-mod-spatialite

After that, running `make` inside the project folder will install all
dependencies and start a test server. You can then log in with username
"admin" and password "password".

For more detailled instructions, see the [developer
documentation](https://git.mpib-berlin.mpg.de/castellum/castellum/-/tree/main/docs).

## Release Schedule

-   Minor releases are published roughly every three months
-   Beta releases might be published to offer previews on new features
-   Bug fix releases are published on demand

## Links

-   Contact: castellum@mpib-berlin.mpg.de
-   Demo: https://castellum-demo.mpib-berlin.mpg.de
-   Source code: https://git.mpib-berlin.mpg.de/castellum/castellum/
-   Releases: https://git.mpib-berlin.mpg.de/castellum/castellum/-/releases
    ([feed](https://git.mpib-berlin.mpg.de/castellum/castellum/-/tags?format=atom))
-   End-user documentation: https://castellum.mpib.berlin/documentation/en/
-   Code of conduct: https://www.mpg.de/11961177/code-of-conduct-en.pdf
