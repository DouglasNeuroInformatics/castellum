# Deployment

## Familiarize yourself with Django

Castellum is first and foremost a Django project. The [Django
documentation](https://docs.djangoproject.com/en/stable/howto/deployment/)
has extensive guidance on how to deploy Django, including several
detailed examples.

This document assumes that you have familiarized yourself with Django
deployment and only explains the pieces that are specific to Castellum.

## Before you start

-   Decide whether you want to install Castellum manually or use a
    docker image. Using the docker image saves you some steps in the
    installation process, but brings its own complexity. We recommend to
    use docker if you already have experience with it.
-   Decide on a database setup. Castellum splits information into two
    databases for enhanced security. This mechanism is most effective if
    those two databases are physically separated. See also the section
    on backups in this document.
-   Decide which optional features you want to use. They are described
    in separte documents.
    -   geo filters
    -   street autocompletion
-   Come up with a migration strategy for legacy systems.
-   You will also need
    -   Linux server with root access
    -   Domain name and TLS certificate
    -   SMTP details
    -   LDAP details (optional)

## Example

An example deployment configuration using docker, uWSGI, PostgreSQL, and
LDAP is located in `docs/deployment/example/`. You can try this
configuration yourself by executing the `start.sh` script in that
folder. Pass `--demo` to automatically create demo content.

## Authentication

We recommend that you integrate Castellum with your existing
authentication system. For example, you could use
[django-auth-ldap](https://django-auth-ldap.readthedocs.io/) to
integrate with an existing LDAP setup. Please refer to the linked
documentation for details on the configuration.

In addition to that, you must set expiration dates for accounts. That is
possible from the admin UI or with the `django-admin activate_user`
command.

## Security

Since Castellum processes special categories of data according to GDRP,
additional security measures are required. While we try to do as much as
possible, not all of these measures can be implemented in the
application itself.

These are some additional security measures we strongly recommend:

-   Use HTTPS only
-   [Restrict access by IP address](https://nginx.org/en/docs/http/ngx_http_access_module.html)

Also see the [django documentation on
security](https://docs.djangoproject.com/en/2.2/topics/security/).

## Backups

Of course it is important to backup the database. Since everything is
stored in a regular PostgreSQL, you should be able to employ your
existing backup solution.

However, you should coordinate with the data protection officer to
discuss the implications for data protection, e.g. [deletion of subject
data](https://castellum.mpib.berlin/documentation/en/guides/subject-management.html#delete-a-subject).
We recommend to keep backups only for a short amount of time (e.g. 14
days) and inform subjects about the date when all their data, including
backups, will be deleted.

## Cron jobs

There are some regular tasks that should be executed independently from
user requests. We provide the following management commands for that:

-   `clearsessions`: Delete expired sessions.
-   `cleanup_media`: Delete unused uploaded files.
-   `cleanup_availability`: Remove obsolete "not available until"
    entries.
-   `cleanup_underage_consents`: Remove recruitment consents for
    underage subjects 2 years after they have come of age.
-   `cleanup_filter_trials`: Delete filter trials as they are meant to be
    used only once.
-   `notify_to_be_deleted`: Automatically notify about content that
    should be deleted.
-   `notify_sessions_end`: Remind study members to finish a study when
    sessions end.
-   `send_appointment_reminders`: Send email reminders to subjects with
    upcoming appointments. If the subjects have no email address, a note
    is sent to the respective study coordinators instead.

## Initial setup

After installing Castellum on your server there are some more steps
before you can start using it:

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

## Updates

After updating to a new version of Castellum it is usually sufficient to
run `django-admin migrateall`. Any additional steps that are
required will be mentioned in the release notes.
