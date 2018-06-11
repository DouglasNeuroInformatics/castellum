import os

import ldap
from django_auth_ldap.config import LDAPSearch

from .default import *


# FIXME: These values need to be changed
SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db_default',
    },
    'subject_management': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db_subject_management',
    }
}

ALLOWED_HOSTS = ['*']

# LDAP
# See https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

AUTH_LDAP_SERVER_URI = 'ldap://ldap'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'admin'
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org', ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
