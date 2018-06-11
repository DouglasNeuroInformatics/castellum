import os

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap4',

    'castellum_auth',
    'subject_management',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'castellum_auth.middlewares.UserExpirationMiddleware',
    'castellum_auth.middlewares.AutoLogoutMiddleware',
]

ROOT_URLCONF = 'castellum_core.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'castellum_core.wsgi.application'


DATABASE_ROUTERS = [
    'subject_management.routers.SubjectManagementRouter',
]

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = 'castellum_auth.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

LOGOUT_TIMEOUT_DEFAULT = timezone.timedelta(seconds=15 * 60)


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]


# Static files (CSS, JavaScript, Images)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
]

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

NPM_ROOT_PATH = os.path.dirname(BASE_DIR)

NPM_FILE_PATTERNS = {
    'bootstrap': ['dist/css/bootstrap.min.css'],
}

# adapt message classes for bootstrap

from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'light',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}


"""
Some notes on the logging configuration:

-   Loggers are hierarchical, so everything eventually ends up at ''.
-   Most logger correspond to modules (e.g. django.server).
-   'monitoring' is our custom logger namespace to monitor user behavior.
-   'django.server' is the development server. It is not used in production.
-   'django' logs to console by default. It is listed here only to remove that handler
    (as this is already covered by '').

See also https://docs.djangoproject.com/en/2.0/topics/logging/

"""
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        }
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'debug-file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'monitoring-file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'monitoring.log'),
            'formatter': 'verbose',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'loggers': {
        '': {
            'handlers': ['debug-file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': [],
            'level': 'DEBUG',
            'propagate': True,
        },
        'monitoring': {
            'handlers': ['monitoring-file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}


CASTELLUM_LOCK_USER_CONTACT = 'admin@example.com'
CASTELLUM_LOCK_USER_NOTIFICATION_SUBJECT = _('[Castellum] Suspicious activity')
CASTELLUM_LOCK_USER_NOTIFICATION_TEXT = _("""Dear {username},

your castellum account has been locked due to suspicious activity.

Please contact {contact}.
""")
