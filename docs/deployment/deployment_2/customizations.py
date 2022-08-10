#
# Exemplary Castellum settings file. See also castellum/docs/deployment_1/settings.py
#
# Lines that need to be modified based on your setup are marked CHANGEME
import os
import ldap
from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType

from .default import *

# Define hosts than can connect
ALLOWED_HOSTS = ['.mydomain.org','192.168.10.*'] # CHANGEME

# People who get code error notifications in production
# CHANGEME
ADMINS = [('admin1', 'admin1@mydomain.org'),
          ('admin2', 'admin2@mydomain.org')]

# People who get notified of broken links
# CHANGEME
MANAGERS = [('manager1', 'manager1@mydomain.org'),
            ('manager2', 'manager2@mydomain.org')]

# Logging setup. If `DEBUG` is `True`, log-levels are set to `DEBUG` and
# the monitoring file `/var/log/castellum_monitoring.log` keeps track of
# user activity. See docs/deployment_2/guide.md for more details.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s'
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'console-debug': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'monitoring-file': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': '/var/log/castellum_monitoring.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        # 'monitoring' is our custom logger namespace to identify and
        # retrace suspicious user behavior. It contains potentially
        # sensitive information (e.g. subject search terms). Monitoring
        # logs will not be created unless configured.
        'monitoring': {
            'handlers': ['monitoring-file'],
            'propagate': False,
        },
        'castellum': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django': {
            'handlers': ['console-debug'],
            'propagate': True,
        },
        'django_auth_ldap': {
            'handlers': ['console-debug'],
            'propagate': True,
        },
    },
}

# Get relevant credentials from env vars
SECRET_KEY = os.environ["DJANGO_SECRET"]
db_default_pw = os.environ["DB_DEFAULT_PW"]
db_contacts_pw = os.environ["DB_CONTACTS_PW"]
bind_pw = os.environ["LDAP_BIND_PW"]

# Database setup. NOTE: The values of `NAME` and `USER` given here have to match
# the actual database name and user set in postgres! See docs/deployment_2/guide.md
# for more details.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castellum_default',
        'USER': 'castellum_default_user',
        'PASSWORD': db_default_pw,
        'HOST': 'localhost',
    },
    'contacts': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castellum_contacts',
        'USER': 'castellum_contacts_user',
        'PASSWORD': db_contacts_pw,
        'HOST': 'castellum-db', # CHANGEME
    },
}

# LDAP setup.
AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')
AUTHENTICATION_BACKENDS.append('django.contrib.auth.backends.ModelBackend')

# CHANGEME Everything below must be adapted to your organization's LDAP setup
# See https://django-auth-ldap.readthedocs.io for details about each setting
AUTH_LDAP_SERVER_URI = 'ldap://auth-sv'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = bind_pw
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org', ldap.SCOPE_SUBTREE, "sAMAccountName=%(user)s")
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(group_lookup, ldap.SCOPE_SUBTREE, "(objectCategory=Group)")
AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300 # in seconds

# Use nginx to serve uploaded files
PROTECTED_MEDIA_SERVER = 'nginx'

# Email settings
DEFAULT_FROM_EMAIL = 'Subject Recruitment at MyDomain <sr@mydomain.org>' # CHANGEME
SERVER_EMAIL = 'root@castellum-sv' # CHANGEME
EMAIL_HOST = 'smtp.mydomain.org' # CHANGEME
EMAIL_PORT = 587
EMAIL_USE_TLS = True
CASTELLUM_GDPR_NOTIFICATION_TO = ['data-protection@mydomain.org'] # CHANGEME
CASTELLUM_STUDY_STATUS_NOTIFICATION_TO = ['pr@mydomain.org'] # CHANGEME
CASTELLUM_API_ENABLED = False

# If you want to allow external services to automatically add subjects
# to the database you need to write a custom script. However, in most
# cases it makes sense to add a review step (e.g. to detect duplicates).
#
# In that case, instead of creating instances of ``Subject`` and
# ``Contact`` directly, it is recommended to use
# ``SubjectCreationRequest`` and ``ContactCreationRequest`` instead.
#
# This option enables the related review UI (available from the
# maintenance dashboard).
CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED = False

# Path to a cover letter template
# Must be in .docx format
# The placeholders "{name}", "{address1}", and "{address2}" will be replaced.
CASTELLUM_COVERLETTER_TEMPLATE = ''
# CASTELLUM_COVERLETTER_TEMPLATE = BASE_DIR / 'subjects' / 'fixtures' / 'demo_coverletter.docx'
