import os

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from castellum.pseudonyms.generators import md5


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrap4',
    'phonenumber_field',
    'parler',

    'castellum.utils',
    'castellum.castellum_auth',
    'castellum.subjects',
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

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

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
    "castellum.studies.backends.StudyPermissionBackend",
]

AUTH_USER_MODEL = 'castellum_auth.User'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

LOGOUT_TIMEOUT_DEFAULT = timezone.timedelta(seconds=15 * 60)


# Internationalization

LANGUAGE_CODE = 'en'

LANGUAGES = [
  ('de', _('German')),
  ('en', _('English')),
]

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

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

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
    'jdenticon': ['dist/jdenticon.min.js'],
    'jquery': ['dist/jquery.min.js'],
    'popper.js': ['dist/umd/popper.min.js'],
    '@fortawesome/fontawesome-free': [
        'css/all.min.css',
        'webfonts/fa-regular-400.eot',
        'webfonts/fa-regular-400.woff2',
        'webfonts/fa-regular-400.woff',
        'webfonts/fa-regular-400.ttf',
        'webfonts/fa-regular-400.svg',
        'webfonts/fa-solid-900.eot',
        'webfonts/fa-solid-900.woff2',
        'webfonts/fa-solid-900.woff',
        'webfonts/fa-solid-900.ttf',
        'webfonts/fa-solid-900.svg',
    ],
}

BOOTSTRAP4 = {
    'set_placeholder': False,
    'success_css_class': None,
}


"""
Some notes on the logging configuration:

-   Loggers are hierarchical, so everything eventually ends up at ''.
-   Most logger correspond to modules (e.g. django.server).
-   'monitoring' is our custom logger namespace to monitor user behavior.
-   'django.server' is the development server. It is not used in production.
-   'django' logs to console by default. It is listed here only to remove that handler
    (as this is already covered by '').

See also https://docs.djangoproject.com/en/stable/topics/logging/

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

# the number of subjects that is added to the recruitment list every time
CASTELLUM_RECRUITMENT_BATCH_SIZE = 15

# used to show the warning message when
# number of users exceeds the number of subjects
# in the contact list of recruitment app
CASTELLUM_RECRUITMENT_SOFT_LIMIT = 40

# variable used to define max number of subjects
# in the contact list of the recruitment app
# max_number_of_subjects = study.min_subjects_count * CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR = 2

# variable is used to define the minimal number of subjects
# required for a normal recruitment process. The variable
# is used to show messages when user creates filters for studies.
CASTELLUM_EXPECTED_SUBJECT_FACTOR = 10

# this constant defines the recommended timespan between one study recruitment call and another one
# from a different study recruitment
CASTELLUM_DAYS_BETWEEN_CONTACT_ATTEMPTS = 14

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

CASTELLUM_FILE_UPLOAD_MAX_SIZE = 5000000

# A function that generates a random pseudonym.
# () -> str (maximum 64 chars)
CASTELLUM_PSEUDONYM_GENERATE = md5.generate

# A function that raises a ValidationError if the pseudonym is invalid.
#
# Returns a *cleaned* pseudonym. This can be used to implement
# auto-correction. But in most cases this will be the same as the input
# value.
#
# See also https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.Field.clean
CASTELLUM_PSEUDONYM_CLEAN = md5.clean
