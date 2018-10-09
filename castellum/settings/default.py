import os

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    'phonenumber_field',

    'castellum.utils',
    'castellum.castellum_auth',
    'castellum.pseudonyms',
    'castellum.recruitment',
    'castellum.studies',
    'castellum.contacts',
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

    'castellum.castellum_auth.middlewares.UserExpirationMiddleware',
    'castellum.castellum_auth.middlewares.AutoLogoutMiddleware',
    'castellum.castellum_auth.middlewares.UserLanguageMiddleware',
]

ROOT_URLCONF = 'castellum.urls'


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

WSGI_APPLICATION = 'castellum.wsgi.application'


DATABASE_ROUTERS = [
    'castellum.contacts.routers.ContactsRouter',
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
LOGIN_URL = '/login/'

LOGOUT_TIMEOUT_DEFAULT = timezone.timedelta(seconds=15 * 60)


# Internationalization

LANGUAGE_CODE = 'en-us'

LANGUAGES = [
  ('de', _('German')),
  ('en', _('English')),
]

TIME_ZONE = 'Europe/Berlin'

PHONENUMBER_DEFAULT_REGION = 'DE'

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
    'bootstrap': [
        'dist/css/bootstrap.min.css',
        'dist/js/bootstrap.min.js'
    ],
    'bootstrap-datepicker': [
        'dist/css/bootstrap-datepicker3.min.css',
        'dist/js/bootstrap-datepicker.min.js',
        'dist/locales/bootstrap-datepicker.de.min.js',
    ],
    'jquery': ['dist/jquery.min.js'],
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

BOOTSTRAP4 = {
    'set_placeholder': False,
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
if os.access('/log', os.W_OK):
    LOG_DIR = '/log'
else:
    LOG_DIR = BASE_DIR

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
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
        'debug-file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'formatter': 'verbose',
        },
        'monitoring-file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'monitoring.log'),
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

# used to show the warning message when
# number of users exceeds the number of subjects
# in the contact list of recruitment app
CASTELLUM_RECRUITMENT_SOFT_LIMIT = 40

# variable used to define max number of subjects
# in the contact list of the recruitment app
# max_number_of_subjects = study.min_subjects_count * CASTELLUM_MULTIPLE_FACTOR
CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR = 2

CASTELLUM_LOCK_USER_CONTACT = 'admin@example.com'
CASTELLUM_LOCK_USER_NOTIFICATION_SUBJECT = '[Castellum] Verdächtige Aktivität / Suspicious activity'
CASTELLUM_LOCK_USER_NOTIFICATION_TEXT = """(English version below)

Liebe/r Castellum Nutzer/in,

Ihr Castellum-Konto wurde wegen verdächtiger Aktivitäten gesperrt.

Bitte kontaktieren Sie {contact}.


* * * * * * * * * * * *

Dear castellum user,

your castellum account has been locked due to suspicious activity.

Please contact {contact}.
"""
CASTELLUM_UNLOCK_USER_NOTIFICATION_SUBJECT = (
    '[Castellum] Verdächtige Aktivität geklärt / Suspicious activity resolved'
)
CASTELLUM_UNLOCK_USER_NOTIFICATION_TEXT = """(English version below)

Liebe/r Castellum Nutzer/in,

Ihr Castellum-Konto wurde wieder freigegeben.


* * * * * * * * * * * *

Dear castellum user,

your castellum account has been unlocked.
"""
