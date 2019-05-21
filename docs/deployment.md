# Deployment

Castellum is a django project. You should refer to the [django
documentation](https://docs.djangoproject.com/en/2.0/howto/deployment/)
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

Since Castellum stores user-related data, additional security measures
are required. While we try to do as much as possible, not all of these
measures can be implemented in the application itself.

These are some additional security measures we strongly recommend:

-   Use HTTPS only
-   [Restrict access by IP address](https://nginx.org/en/docs/http/ngx_http_access_module.html)
-   Authentication (e.g. LDAP) is typically only checked on login. To
    force regular re-authentication we recommend to logout all users
    regulary, e.g. every night. We provide the command `manage.py
    clear_sessions` for that.
