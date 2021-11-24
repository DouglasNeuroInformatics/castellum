import ldap
from django_auth_ldap.config import LDAPSearch

from .default import *

# FIXME: These values need to be changed
SECRET_KEY = 'CHANGEME'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'CHANGEME',
        'HOST': 'db_scheduler',
    },
}

ALLOWED_HOSTS = ['*']

# LDAP
# See https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
]

AUTH_LDAP_SERVER_URI = 'ldap://ldap:3389'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'admin'
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org', ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
}

API_TOKEN = 'CHANGEME'
