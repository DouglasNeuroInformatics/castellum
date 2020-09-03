import datetime
import os

from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta

from castellum.pseudonyms.generators import md5

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = []

PRODUCTION = False


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrap4',
    'phonenumber_field',
    'parler',
    'stronghold',

    'castellum.utils',
    'castellum.castellum_auth',
    'castellum.subjects',
    'castellum.pseudonyms',
    'castellum.recruitment',
    'castellum.execution',
    'castellum.studies',
    'castellum.contacts',
    'castellum.data_protection',
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

    'stronghold.middleware.LoginRequiredMiddleware',

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
    'castellum.utils.routers.Router',
]

APP_DB_ROUTER = {
    'contacts': 'contacts',
    'geofilters': 'contacts',
}

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

LOGOUT_TIMEOUT_DEFAULT = datetime.timedelta(seconds=15 * 60)


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
    'fullcalendar-scheduler': [
        'main.js',
        'main.css',
        'locales/de.js',
    ],
}

BOOTSTRAP4 = {
    'set_placeholder': False,
    'success_css_class': None,
}

AXES_LOCKOUT_TEMPLATE = 'axes-lockout.html'


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
        },
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

# Secondary language in emails for readers who do not understand the
# primary language
CASTELLUM_FALLBACK_LANGUAGE = 'en'
CASTELLUM_FALLBACK_LANGUAGE_MARKERS = (
    '++++ FOR ENGLISH VERSION SEE BELOW ++++',
    '++++ ENGLISH VERSION ++++',
)

CASTELLUM_ENABLE_STUDY_EXPORT = True

# timespan a subject should be allowed to remain in the database without
# consent given
CASTELLUM_CONSENT_REVIEW_PERIOD = relativedelta(weeks=2)

# maximum timespan a subject should be allowed to remain in the database
# after requesting to be deleted
CASTELLUM_SUBJECT_DELETION_PERIOD = datetime.timedelta(days=30)

CASTELLUM_APPOINTMENT_REMINDER_PERIOD = datetime.timedelta(days=2)
CASTELLUM_APPOINTMENT_MAIL_SUBJECT = "Reminder: You have an appointment"
CASTELLUM_APPOINTMENT_MAIL_BODY = (
    "Guten Tag {subject},\n\n"
    "wir möchten Sie an ihren Termin in der Studie {study} am {date} erinnern.\n"
    "Falls Sie absagen oder den Termin verschieben möchten, so melden Sie sich "
    "bitte bei {reply_to}.\n\n"
    "Mit freundlichen Grüßen\ndas Rekrutierungsteam"
)
CASTELLUM_APPOINTMENT_MAIL_BODY_EN = (
    "Dear {subject},\n\nwe would like to kindly remind you of your appointment in "
    "study {study} on {date}.\n"
    "If you wish to cancel or postpone, please get in touch with {reply_to}.\n\n"
    "Sincerely yours\nthe recruitment team"
)
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_SUBJECT = "Appointment reminders for {study}"
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY = (
    "The following subjects have upcoming appointments, but could not be reached by email. "
    "Please contact them by other means to remind them of their appointment:\n\n{urls}"
)

# the number of subjects that is added to the recruitment list every time
CASTELLUM_RECRUITMENT_BATCH_SIZE = 15

# settings for sending recruitment mails (defaults to general settings)
# Complete example:
# {
#     'from_email': 'Castellum <castellum@example.com>',
#     'language': 'en',
#     'subject_prefix': '[Castellum] ',
#     'signature': '\n\n-- \nAutomatically send by castellum',
#     'connection': {
#         # The full list of options is available at
#         # https://docs.djangoproject.com/en/stable/topics/email/#django.core.mail.get_connection
#         'username': 'mailuser',
#         'password': 'mailpassword',
#     }
# }
CASTELLUM_MAIL = {
    'recruitment': {
        'language': 'de',
    },
    'internal': {
        'subject_prefix': '[Castellum] ',
    },
}

# used to show the warning message when
# number of users exceeds the number of subjects
# in the contact list of recruitment app
CASTELLUM_RECRUITMENT_SOFT_LIMIT = 40

# variable used to define max number of subjects
# in the contact list of the recruitment app
# max_number_of_subjects = study.min_subject_count * CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR = 2

# variable is used to define the minimal number of subjects
# required for a normal recruitment process. The variable
# is used to show messages when user creates filters for studies.
CASTELLUM_EXPECTED_SUBJECT_FACTOR = 10

# this constant defines the recommended timespan between one contact
# attempt and another one from a different study recruitment
CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS = relativedelta(weeks=2)

CASTELLUM_DELETE_NOTIFICATION_TO = None
CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_SUBJECT = 'Subject export'
CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY = 'The following subject should be exported: {url}'
CASTELLUM_DELETE_SUBJECT_NOTIFICATION_SUBJECT = 'Subject deletion'
CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY = 'The following subject should be deleted: {url}'

CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT = 'Upcoming appointment changed'
CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY = """
Upcoming appointments for a participant in the study "{study}" have changed:

{changes}

Participant details: {participation_url}
Study calendar: {calendar_url}
"""

CASTELLUM_FILE_UPLOAD_MAX_SIZE = 5000000

# A function that generates a random pseudonym.
# (bits: int) -> str (maximum 64 chars)
# First argument is a hint about the number of random bits that should be included.
CASTELLUM_PSEUDONYM_GENERATE = md5.generate

# A function that raises a ValidationError if the pseudonym's format is invalid.
#
# Returns a *cleaned* pseudonym. This can be used to implement
# auto-correction. But in most cases this will be the same as the input
# value.
#
# See also https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.Field.clean
CASTELLUM_PSEUDONYM_CLEAN = md5.clean

CASTELLUM_STUDY_DOMAIN_BITS = 20

# Path to a cover letter template
# Must be in .docx format
# The placeholders "{name}", "{address1}", and "{address2}" will be replaced.
CASTELLUM_COVERLETTER_TEMPLATE = None

CASTELLUM_FULL_AGE = 16

# Criteria that apply to all studies
CASTELLUM_GENERAL_EXCLUSION_CRITERIA = ''
