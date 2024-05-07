# Castellum

The General Data Protection Regulation (GDPR) mandates that
organizations maintain a comprehensive inventory of the data they hold
on individuals. This requirement poses challenges within research
institutes, where researchers traditionally have a high degree of
autonomy in organizing their work.

Castellum addresses this by serving as a centralized repository,
enabling researchers to disclose the individuals from whom they have
gathered data. Additionally, Castellum allows to track recruitment
consent for those individuals, thereby creating a recruitment pool for
future research projects.

## Features

-   **GDPR Compliance**: Castellum is a central place where researchers
    disclose the individuals from whom they have gathered data, so that
    requests for access or erasure can be handled efficiently.
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

## Release Schedule

-   Minor releases are published roughly every three months
-   Beta releases might be published to offer previews on new features
-   Bug fix releases are published on demand

## Links

-   Contact: castellum@mpib-berlin.mpg.de
-   Demo: https://castellum.t.mpib-berlin.mpg.de
-   Source code: https://git.mpib-berlin.mpg.de/castellum/castellum/
-   Releases: https://git.mpib-berlin.mpg.de/castellum/castellum/-/releases
    ([feed](https://git.mpib-berlin.mpg.de/castellum/castellum/-/tags?format=atom))
-   End-user documentation: https://castellum.mpib.berlin/documentation/en/
-   Code of conduct: https://www.mpg.de/11961177/code-of-conduct-en.pdf
