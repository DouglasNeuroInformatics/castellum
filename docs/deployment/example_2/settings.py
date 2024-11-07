import os

import ldap
from django_auth_ldap.config import LDAPSearch

from castellum.settings.default import *

# Fetch Django secret key from environment
SECRET_KEY = os.getenv('DJANGO_SECRET')

# ------------------- Customizations ---------------------------
CASTELLUM_SITE_TITLE = 'Castellum Demo'
#
# Optional logo
#
# The logo will be displayed next to the title as a 40x40 square.
# The logo most be available from the same origin.
# All other origins are blocked for security reasons.
CASTELLUM_SITE_LOGO = '/static/images/my_icon.png'

# You can overwrite the primary color and its two darker shades.
# Default: ['#0d6efd', '#0b5ed7', '#0a58ca']
BOOTSTRAP_THEME_COLORS = ['#0d6efd', '#0b5ed7', '#0a58ca']

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

# ------------------- Security ---------------------------
# Cookies, encryption and transport security
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_SSL_REDIRECT = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Define hosts than can connect
ALLOWED_HOSTS = ['castellum.example.com', '192.168.10.*']

# Multi-factor setup, see https://github.com/xi/django-mfa3
MFA_SITE_TITLE = CASTELLUM_SITE_TITLE
MFA_DOMAIN = 'castellum.example.com'

# Limit login attempts, see https://django-axes.readthedocs.io/
INSTALLED_APPS.append('axes')
AUTHENTICATION_BACKENDS.insert(0, 'axes.backends.AxesBackend')
MIDDLEWARE.append('axes.middleware.AxesMiddleware')
AXES_IPWARE_META_PRECEDENCE_ORDER = ['HTTP_X_REAL_IP']

# Use nginx to serve uploaded files
PROTECTED_MEDIA_SERVER = 'nginx'
MEDIA_ROOT = '/var/lib/castellum/media'
PROTECTED_MEDIA_URL = '/protected/'
CASTELLUM_FILE_UPLOAD_MAX_SIZE = 5000000

# By default, the monitoring log records all subject searches. This
# allows you to detect users who abuse this feature, e.g. to search for
# famous people.
# On the other hand, the search text usually contains personal
# information such as names and email addresses. It depends on your
# specific threat model whether you want to include this or not.
CASTELLUM_MONITORING_INCLUDE_SEARCH = True

# ------------------- Database Setup ---------------------------
# Only postgres/postgis are officially supported for Castellum.
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
        'HOST': 'castellum-db',
    },
}

# ------------------- Authentication ---------------------------
# Use LDAP, see https://django-auth-ldap.readthedocs.io/
AUTHENTICATION_BACKENDS.append('django_auth_ldap.backend.LDAPBackend')

AUTH_LDAP_SERVER_URI = 'ldap://auth-sv'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = os.getenv('LDAP_BIND_PW')
AUTH_LDAP_USER_QUERY_FIELD = 'username'
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    'dc=example,dc=org',
    ldap.SCOPE_SUBTREE,
    '(|(uid=%(user)s)(mail=%(user)s))',
)
AUTH_LDAP_USER_ATTR_MAP = {
    'username': 'uid',
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}
# Alternatively you can manage permissions directly in LDAP
# See https://django-auth-ldap.readthedocs.io/en/latest/permissions.html#using-groups-directly
# AUTH_LDAP_FIND_GROUP_PERMS = True

# ------------------- Notifications + Logging ---------------------------
# Email settings
DEFAULT_FROM_EMAIL = 'Subject Recruitment at Example <sr@example.com>'
SERVER_EMAIL = 'root@castellum-sv'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# People who get code error notifications in production
ADMINS = [
    ('admin1', 'admin1@example.com'),
    ('admin2', 'admin2@example.com'),
]

CASTELLUM_EMAIL_BASE_URL = 'https://castellum.example.com'
CASTELLUM_GDPR_NOTIFICATION_TO = ['data-protection@example.com']
CASTELLUM_REPORT_NOTIFICATION_TO = ['report@example.com']

# See https://docs.djangoproject.com/en/stable/topics/logging/
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
            'level': 'INFO',
        },
        'monitoring-file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/castellum/monitoring.log',
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
    },
    'root': {
        'handlers': ['console'],
        'level': 'NOTSET',
    },
}
