#
# Exemplary Castellum settings file. See also castellum/docs/example_1/settings.py
#
# Lines that need to be modified based on your setup are marked CHANGEME
import os
import ldap
from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType

from .default import *

#
#  For a full list of settings see castellum/settings/default/__init__.py
#

# ------------------- Security -----------------------------------------
#
# The provided systemd unit ensures that all required environment
# variables are properly sourced and made available
SECRET_KEY = os.getenv('DJANGO_SECRET')

# Database setup. NOTE: The values of `NAME` and `USER` given here have
# to match # the actual database name and user set in postgres! See
# docs/deployment/example_2/README.md for more details.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castellum_default',
        'USER': 'castellum_default_user',
        'PASSWORD': os.getenv('DB_DEFAULT_PW'),
        'HOST': 'localhost',
    },
    'contacts': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'castellum_contacts',
        'USER': 'castellum_contacts_user',
        'PASSWORD': os.getenv('DB_CONTACTS_PW'),
        'HOST': 'castellum-db',                             # CHANGEME
    },
}

# Define hosts than can connect
ALLOWED_HOSTS = ['.example.com', '192.168.10.*']            # CHANGEME

# Setting `PRODUCTION` to `True` prevents the creation of insecure demo content
PRODUCTION = True

# Django security settings, cf. https://docs.djangoproject.com/en/4.1/ref/settings/
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Timeout period for auto-logout
CASTELLUM_LOGOUT_TIMEOUT = datetime.timedelta(seconds=15 * 60)

# Limit login attempts, see https://django-axes.readthedocs.io/
INSTALLED_APPS.append('axes')
AUTHENTICATION_BACKENDS.insert(0, 'axes.backends.AxesBackend')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AXES_META_PRECEDENCE_ORDER = ['HTTP_X_REAL_IP']
AXES_FAILURE_LIMIT = 5                                      # CHANGEME

# Recruiters are not supposed to add excessive numbers of subjects
# After reaching the hard limit, no more subjects can be added.
# max_number_of_subjects = study.min_subject_count * CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR = 2
CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT = math.inf

# Enables some additional views that expose content as JSON
# (see castellum/settings/default/__init__.py for details)
CASTELLUM_API_ENABLED = False

# If external services are allowed to automatically add subjects, enable
# review UI from the maintenance dashboard
# (see castellum/settings/default/__init__.py for details)
CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED = False

# Use nginx to serve uploaded files
PROTECTED_MEDIA_SERVER = 'nginx'
PROTECTED_MEDIA_URL = '/protected/'
CASTELLUM_FILE_UPLOAD_MAX_SIZE = 5000000

# ------------------- User Authentication ------------------------------
#
# LDAP setup.
AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')
AUTHENTICATION_BACKENDS.append('django.contrib.auth.backends.ModelBackend')

# Everything below must be adapted to your organization's LDAP setup,
# see https://django-auth-ldap.readthedocs.io               # CHANGEME
AUTH_LDAP_SERVER_URI = 'ldap://auth-sv'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PW')
AUTH_LDAP_USER_SEARCH = LDAPSearch('dc=example,dc=org,ou=users',
                                    ldap.SCOPE_SUBTREE,
                                    "sAMAccountName=%(user)s")
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('dc=example,dc=org,ou=groups',
                                    ldap.SCOPE_SUBTREE,
                                    "(objectCategory=Group)")
AUTH_LDAP_GROUP_TYPE = NestedActiveDirectoryGroupType()
AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300  # in seconds

# Enforce the use of a second factor for all accounts (for more details
# see https://github.com/xi/django-mfa3)
MIDDLEWARE.append('mfa.middleware.MFAEnforceMiddleware')
MFA_DOMAIN = 'example.com'                                  # CHANGEME
MFA_SITE_TITLE = 'My MFA Title'                             # CHANGEME

# ------------------- Notifications and Monitoring----------------------
#
# Email settings
DEFAULT_FROM_EMAIL = 'Subject Recruitment at Example <sr@example.com>'  # CHANGEME
SERVER_EMAIL = 'root@castellum-sv'                          # CHANGEME
EMAIL_HOST = 'smtp.example.com'                             # CHANGEME
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# People who get code error notifications in production
ADMINS = [                                                  # CHANGEME
    ('admin1', 'admin1@example.com'),
    ('admin2', 'admin2@example.com'),
]

# People who get notified of broken links
MANAGERS = [('Jane Doe', 'jane.doe@example.com'),           # CHANGEME
            ('John Smith', 'john.smith@example.com')]

# People who get notified of data protection issues
CASTELLUM_GDPR_NOTIFICATION_TO = ['gdpr@example.com']

# People who get notified of study status
CASTELLUM_STUDY_STATUS_NOTIFICATION_TO = ['pr@example.com']

# Logging setup
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'monitoring-file': {
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
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ------------------- Customizations -----------------------------------
#
# Optional logo
#
# The logo will be displayed next to the title as a 40x40 square.
# The logo most be available from the same origin.
# All other origins are blocked for security reasons.
#
# Example: '/static/my_logo.svg'
CASTELLUM_SITE_LOGO = None                                  # CHANGEME

# Title displayed on login page
CASTELLUM_SITE_TITLE = 'My Title'                           # CHANGEME

# You can overwrite the primary color and its two darker shades.
# Default: ['#0d6efd', '#0b5ed7', '#0a58ca']
BOOTSTRAP_THEME_COLORS = None                               # CHANGEME

# Internationalization
LANGUAGE_CODE = 'en'
PARLER_LANGUAGES = {
    None: (
        {'code': 'de'},
        {'code': 'en'},
    ),
    'default': {
        'fallback': LANGUAGE_CODE,
    },
}
TIME_ZONE = 'Europe/Berlin'
PHONENUMBER_DEFAULT_REGION = 'DE'

# Texts that apply to all studies
CASTELLUM_GENERAL_RECRUITMENT_TEXT = ''
