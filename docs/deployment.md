# Deployment

Castellum is a django project. You should refer to the [django
documentation](https://docs.djangoproject.com/en/2.0/howto/deployment/) for most questions
concerning deployment.

## Example

An example configuration is included in this repository.  You can execute it with `docker-compose -f
docker-compose.yml -f docker-compose.manage.yml up` inside the `example_deplyment/` folder. It
includes example configuration for Nginx, uWSGI, PostgreSQL, and LDAP.

## Authentication

We recommend that you integrate Castellum with your existing authentication system. For example, you
could use [django-auth-ldap](https://django-auth-ldap.readthedocs.io/) to integrate with an existing
LDAP setup. Please refer to the linked documentation for details on the configuration.

## Security

Since Castellum stores user-related data, additional security measures are required. While we try to
do as much as possible, not all of these measures can be implemented in the application itself.

These are some additional security measures we strongly recommend:

-   Use HTTPS only
-   [Restrict access by IP address](https://nginx.org/en/docs/http/ngx_http_access_module.html)
-   Authentication (e.g. LDAP) is typically only checked on login. To force regular
    re-authentication we recommend to logout all users regulary, e.g. every night. We provide the
    command `manage.py clear_sessions` for that. If you use the provided docker image is already
    included.
