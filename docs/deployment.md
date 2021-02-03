# Deployment

Castellum is a django project. You should refer to the [django
documentation](https://docs.djangoproject.com/en/stable/howto/deployment/)
for most questions concerning deployment.

## Before you start

-   Decide whether you want to install castellum manually or use a
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
-   You will also need
    -   Linux server with root access
    -   Domain name and TLS certificate
    -   SMTP details
    -   LDAP details (optional)

## Example

An example deployment configuration using docker, uWSGI, PostgreSQL, and
LDAP is located in `docs/example_deployment/`. You can try this
configuration yourself by executing the `start.sh` script in that
folder. Pass `--demo` to automatically create demo content.

## Authentication

We recommend that you integrate Castellum with your existing
authentication system. For example, you could use
[django-auth-ldap](https://django-auth-ldap.readthedocs.io/) to
integrate with an existing LDAP setup. Please refer to the linked
documentation for details on the configuration.

## Security

Since Castellum processes special categories of data accrding to GDRP,
additional security measures are required. While we try to do as much as
possible, not all of these measures can be implemented in the
application itself.

These are some additional security measures we strongly recommend:

-   Use HTTPS only
-   [Restrict access by IP address](https://nginx.org/en/docs/http/ngx_http_access_module.html)
-   Authentication (e.g. LDAP) is typically only checked on login. To
    force regular re-authentication we recommend to logout all users
    regulary, e.g. every night. We provide the command `manage.py
    clear_sessions` for that.

Also see the [django documentation on
security](https://docs.djangoproject.com/en/2.2/topics/security/).

## Backups

Of course it important to backup the database. Since everything is
stored in a regular PostgreSQL, you should be able to employ your
existing backup solution.

However, you should coordinate with the data protection officer to
discuss the implications for data protection, e.g. [deletion of subject
data](https://castellum.mpib.berlin/documentation/en/workflows/deleting.html).
We recommend to keep backups only for a short amount of time and inform
subjects about that.

## Cron jobs

There are some regular tasks that should be executed independently from
user requests. We provide the following management commands for that:

-   `clear_sessions`: Delete all sessions to force-logout expired users.
-   `cleanup_media`: Delete unused uploaded files.
-   `notify_to_be_deleted`: Automatically notify about content that
    should be deleted.
-   `send_appointment_reminders`: Send email reminders to subjects with
    upcoming appointments. If the subjects have no email address, a note
    is sent to the respective study coordinators instead.

## Initial setup

After installing castellum on your server there are some more steps
before you can start using it:

1.  Adapt the settings.

2.  Check for some common issues:

        python manage.py check --deploy

3.  Run migrations on all databases:

        python manage.py migrateall

4.  Load recommended data. This is not strictly necessary, but it
    usually makes sense to start from these defaults:

        python manage.py loaddata groups timeslots study_types study_groups resources
        python manage.py create_attribute_descriptions

    **Warning**: If you run this command a second time, the database
    will be reset and all edits will be lost.

5.  Create and activate an initial user. This user can then be used to
    activate (i.e. set expiration dates for) all further users:

        python manage.py createsuperuser --username admin
        python manage.py activate_user admin

## Updates

After updating to a new version of castellum it is usually sufficient to
run `python manage.py migrateall`. Any additional steps that are
required will be mentioned in the release notes.
