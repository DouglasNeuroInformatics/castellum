# Deployment

Castellum is a django project. You should refer to the [django
documentation](https://docs.djangoproject.com/en/stable/howto/deployment/)
for most questions concerning deployment.

## Example

An example deployment configuration using docker, uWSGI, PostgreSQL, and
LDAP is located in `docs/example_deployment/`. You can try this
configuration yourself by executing the `start.sh` script in that
folder.

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

## Cron jobs

There are some regular tasks that should be executed independently from
user requests. We provide the following management commands for that:

-   `clear_sessions`: Delete all sessions to force-logout expired users.
-   `cleanup_media`: Delete unused uploaded files.

## Initial setup

After installing castellum on your server there are some more steps
before you can start using it:

1.  Run migrations on all databases:

        python manage.py migrateall

2.  Sync pseudonym domains from settings to the database:

        python managae.py sync_domains

    **Note**: You need to re-run this if you change the `DOMAINS`
    setting. Otherwise domain reuse might occur which could leak
    pseudonyms.

3.  Load sample data. This is not strictly necessary, but it usually
    makes sense to start from these defaults:

        python manage.py loaddata sample_groups timeslots study_types
        python manage.py create_sample_attribute_descriptions

    **Warning**: If you run this command a second time, the database
    will be reset and all edits will be lost.

4.  Create and activate an initial user. This user can then be used to
    activate (i.e. set expiration dates for) all further users:

        python manage.py createsuperuser --username admin
        python manage.py activate_user admin
