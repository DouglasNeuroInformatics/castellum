# Setup and Deployment

Castellum offers several options to get started. You can either quickly
spin up a test-server to get a first impression of its features or go
through the full deployment steps to set up a production-ready instance.

## Introduction

Castellum is first and foremost a Django project. The [Django
documentation](https://docs.djangoproject.com/en/stable/howto/deployment/)
has extensive guidance on how to deploy Django, including several
detailed examples.

This document assumes that you have familiarized yourself with Django
deployment and only explains the pieces that are specific to Castellum.
In addition, familiarity with web servers and databases in general is
beneficial.

## Quickstart

The following commands install all required dependencies and start a
local test-server (on Ubuntu) to try/test Castellum:

    sudo apt install python3-pip python3-venv npm make gettext sqlite3 libmagic1 gdal-bin libsqlite3-mod-spatialite
    cd castellum
    make  # start castellum

You can login with user "admin" and password "password".

**Note** This test-server is solely intended for demonstration and
development purposes. Do **not** use this setup for production!

## Before You Actually Start

The data processed and stored by Castellum represent special categories
of personal data according to Article 9 of the European Union's General
Data Protection Regulation (GDPR). Therefore, special requirements
pertaining to user authentication, security, backups and maintenance
have to be taken into consideration when setting up a production
instance of Castellum.

### Authentication

We recommend integrating Castellum with existing authentication systems.
For example, you could use
[django-auth-ldap](https://django-auth-ldap.readthedocs.io/) to
integrate with an existing LDAP setup. Please refer to the linked
documentation for details on the configuration.

In addition to that, you must set expiration dates for accounts. That is
possible from the admin UI or with the `django-admin activate_user`
command.

### Security

Castellum has been carefully designed to implement technical and
organisational measures to protect all personal data processed and
stored by it. However, not all of these measures can be implemented in
the application itself.

These are some additional security measures we strongly recommend:

-   Use HTTPS transport encryption
-   [Restrict access by IP address](https://nginx.org/en/docs/http/ngx_http_access_module.html)
-   Enable [django-axes](https://django-axes.readthedocs.io/) to block
    brute-force attacks on API views
-   Enforce the use of a second factor for user authentication via
    [django-mfa3](https://github.com/xi/django-mfa3)

Also see the [django documentation on
security](https://docs.djangoproject.com/en/2.2/topics/security/).

### Backups

As with any other database application, having a database backup
strategy in place is important. We recommend using PostgreSQL, which
permits employing existing backup solutions.

However, you should coordinate with your local data protection officer
to discuss the implications for data protection, e.g.
[deletion of subject data](https://castellum.mpib.berlin/documentation/en/guides/subject-management.html#delete-a-subject).
We recommend to keep backups only for a short amount of time (e.g. 14
days) and inform subjects about the date when all their data, including
backups, will be deleted.

### Maintenance - Cron Jobs

There are some regular tasks that should be executed independently from
user requests. We provide the following management commands for that:

-   `clearsessions`: Delete expired sessions.
-   `cleanup_media`: Delete unused uploaded files.
-   `cleanup_availability`: Remove obsolete "not available until"
    entries.
-   `cleanup_underage_consents`: Remove recruitment consents for
    underage subjects 2 years after they have come of age.
-   `cleanup_filter_trials`: Delete filter trials as they are meant to
    be used only once.
-   `notify_to_be_deleted`: Automatically notify about content that
    should be deleted.
-   `notify_sessions_end`: Remind study members to finish a study when
    sessions end.
-   `send_appointment_reminders`: Send email reminders to subjects with
    upcoming appointments. If the subjects have no email address, a note
    is sent to the respective study coordinators instead.

## Deployment Types

Castellum may be deployed containerized (via Docker) or manually. Using
the Docker image saves some steps in the installation process, but
brings its own complexity. We recommend to use Docker if you already
have experience with it. In both scenarios, however, some things need to
be considered before deploying:

-   **Prerequisites** You will need
    -   Linux server with root access
    -   Domain name and TLS certificate
    -   SMTP details
    -   LDAP details (optional)
-   **Database Setup** Castellum splits information into two databases for
    enhanced security. This mechanism is most effective if those two
    databases are *physically* separated.
-   **Optional Features** Decide which optional features you want to use.
    They are described in the following separate documents:
    -   [geo filters](geo.md)
    -   [street autocompletion](street_autocompletion.md)

Once you come to a decision on the above mentioned points, please refer
to the corresponding sub-sections for details about the respective
deployment strategy.

### Initial setup

After installing Castellum on your server there are some additional
steps before you can start using it.

1.  Adapt the settings. See `castellum/settings/default/` for the full
    list of available settings.

    The most important ones are listed in the [django deployment
    checklist](https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/).
    You should also set `PRODUCTION = True` to disable Castellum's demo
    features.

2.  Check for some common issues:

        django-admin check --deploy

3.  Run migrations on all databases:

        django-admin migrateall

4.  Load recommended data. This is not strictly necessary, but it
    usually makes sense to start from these defaults:

        django-admin loaddata groups study_types study_groups resources attribute_descriptions

    **Warning**: If you run this command a second time, the database
    will be reset and all edits will be lost.

5.  Create and activate an initial user. This user can then be used to
    activate (i.e. set expiration dates for) all further users:

        django-admin createsuperuser --username admin
        django-admin activate_user admin

    See the [end-user documentation](https://castellum.mpib.berlin/documentation/en/roles.html#administrator)
    for further information.

### Deployment Examples

#### Example 1

An example deployment configuration using Docker, uWSGI, PostgreSQL, and
LDAP is located in [Example 1](example_1/README.md). You can try this
configuration yourself by executing the `start.sh` script in that
folder. Pass `--demo` to automatically create demo content.

#### Example 2

A setup guide for a manual deployment of Castellum is provided in
[Example 2](example_2/README.md)

## Updates

After updating to a new version of Castellum it is usually sufficient to
run `django-admin migrateall`. Any additional steps that are required
will be mentioned in the release notes.
