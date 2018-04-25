import ldap
import os
from django_auth_ldap.config import LDAPSearch

from .default import *


# FIXME: These values need to be changed
SECRET_KEY = 'i#$kwk(s24ysn+l%+c!*z9u4+45)oex!-s#!bux#wf2pv2cc0d'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

ALLOWED_HOSTS = [
    'localhost',
]

# LDAP
AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

host = os.environ.get("LDAP_HOST", "ldap://localhost")
distinguised_name = os.environ.get("LDAP_DISTINGUISHED_NAME", "dc=example,dc=org")
username = os.environ.get("LDAP_USERNAME", "cn=admin," + distinguised_name)
password = os.environ.get("LDAP_PASSWORD", "admin")

AUTH_LDAP_SERVER_URI = host
AUTH_LDAP_BIND_DN = username
AUTH_LDAP_BIND_PASSWORD = password
AUTH_LDAP_USER_SEARCH = LDAPSearch(distinguised_name, ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
