import datetime
import math
import os
from pathlib import Path

import castellum_pseudonyms
from dateutil.relativedelta import relativedelta

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = []

# Set this to True to prevent creating insecure demo content in production
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
    'castellum.appointments',
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
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'castellum.utils.context_processors.get_settings',
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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

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

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_HTTPONLY = True

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

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']


# Static files (CSS, JavaScript, Images)

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'npm.finders.NpmFinder',
]

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'collected_static'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

NPM_ROOT_PATH = BASE_DIR.parent

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


if os.access('/log', os.W_OK):
    LOG_DIR = Path('/log')
else:
    LOG_DIR = BASE_DIR

# See https://docs.djangoproject.com/en/stable/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s %(message)s'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'monitoring-file': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'monitoring.log',
            'formatter': 'verbose',
        },
        'django.server': {
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # 'monitoring' is our custom logger namespace to monitor user behavior.
        # It contains potentially sensitive information (e.g. subject search terms).
        'monitoring': {
            'handlers': ['monitoring-file'],
            'level': 'INFO',
        },
        # 'django.server' is the development server. It is not used in production.
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Secondary language in emails for readers who do not understand the
# primary language
CASTELLUM_FALLBACK_LANGUAGE = 'en'
CASTELLUM_FALLBACK_LANGUAGE_MARKERS = (
    '++++ FOR INFORMATION IN ENGLISH SEE BELOW ++++',
    '++++ INFORMATION IN ENGLISH ++++',
)

CASTELLUM_ENABLE_STUDY_EXPORT = True

# timespan a subject should be allowed to remain in the database without
# consent given
CASTELLUM_CONSENT_REVIEW_PERIOD = relativedelta(weeks=2)

# timespan a subject should be allowed to remain in the database
# after requesting to be deleted
CASTELLUM_SUBJECT_DELETION_PERIOD = datetime.timedelta(days=30)

CASTELLUM_APPOINTMENT_REMINDER_PERIOD = datetime.timedelta(days=2)
CASTELLUM_APPOINTMENT_MAIL_SUBJECT = "Reminder: You have an appointment"
CASTELLUM_APPOINTMENT_MAIL_BODY = (
    "Guten Tag {name},\n\n"
    "wir möchten Sie an ihren Termin in der Studie {study} am {date} erinnern.\n"
    "Falls Sie absagen oder den Termin verschieben möchten, so melden Sie sich "
    "bitte bei {reply_to}.\n\n"
    "Zusätzliche Informationen:\n"
    "{session_reminder_text}\n\n"
    "Mit freundlichen Grüßen\ndas Rekrutierungsteam"
)
CASTELLUM_APPOINTMENT_MAIL_BODY_EN = (
    "Dear {name},\n\nwe would like to kindly remind you of your appointment in "
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

# settings for sending mails (defaults to general settings)
# Complete example:
# {
#     'from_email': 'Castellum <castellum@example.com>',
#     'language': 'en',
#     'subject_prefix': '[Castellum] ',
#     'recipients_text': '\n\nThis email was sent to: {}',
#     'signature': '\n\n-- \nAutomatically sent by castellum',
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
        'recipients_text': '\n\nDiese E-Mail wurde gesendet an: {}',
    },
    'internal': {
        'subject_prefix': '[Castellum] ',
    },
}

# Recruiters are not supposed to add excessive numbers of subjects to
# the recruitment list. After reaching the soft limit, a warning is
# shown. After reaching the hard limit, no more subjects can be added.
# max_number_of_subjects = study.min_subject_count * CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
CASTELLUM_RECRUITMENT_SOFT_LIMIT = 40
CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR = 2
CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT = math.inf

# Used to determine whether there are enough potential subjects to
# complete the study. If not, a warning is shown during filter creation.
CASTELLUM_EXPECTED_SUBJECT_FACTOR = 10

# recommended timespan between one contact attempt and another one from
# a different study recruitment
CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS = relativedelta(weeks=2)

CASTELLUM_DELETE_NOTIFICATION_TO = ''
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

# Email addresses for announcing new public studies
CASTELLUM_STUDY_STATUS_NOTIFICATION_TO = []
CASTELLUM_STUDY_STATUS_NOTIFICATION_SUBJECT = '[{study}] Study status changed'
CASTELLUM_STUDY_STATUS_NOTIFICATION_BODY = """Study details of {name}:

Status: {status}
Previous status: {previous_status}

Contact person: {contact_person}
Email: {email}
Phone: {phone},
Session types: {session_types}
Scheduled runtime: {sessions_start} - {sessions_end}
Excluded studies: {excluded_studies}
Filters:
{filters}

Recruitment text:
{recruitment_text}

Inclusion/Exclusion criteria:
{exclusion_criteria}

"""

CASTELLUM_FILE_UPLOAD_MAX_SIZE = 5000000

# A function that generates a random pseudonym.
# (bits: int) -> str (maximum 64 chars)
# First argument is a hint about the number of random bits that should be included.
CASTELLUM_PSEUDONYM_GENERATE = castellum_pseudonyms.generate

# A function that raises a ValidationError if the pseudonym's format is invalid.
#
# Returns a *cleaned* pseudonym. This can be used to implement
# auto-correction. But in most cases this will be the same as the input
# value.
#
# See also https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.Field.clean
CASTELLUM_PSEUDONYM_CLEAN = castellum_pseudonyms.clean

CASTELLUM_STUDY_DOMAIN_BITS = 20
CASTELLUM_SESSION_DOMAIN_BITS = 20

# Path to a cover letter template
# Must be in .docx format
# The placeholders "{name}", "{address1}", and "{address2}" will be replaced.
CASTELLUM_COVERLETTER_TEMPLATE = ''

# If this is set, this attribute will automatically be filled from Contact.date_of_birth
CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = None

CASTELLUM_FULL_AGE = 16

# Texts that apply to all studies
CASTELLUM_GENERAL_EXCLUSION_CRITERIA = ''
CASTELLUM_GENERAL_RECRUITMENT_TEXT = ''

# Default exporter used for attributes.
# Currently available options are
# - 'castellum.recruitment.attribute_exporters.JSONExporter'
# - 'castellum.recruitment.attribute_exporters.BIDSExporter'
# You can also implement your own if required.
# See castellum/recruitment/attribute_exporters.py for details
CASTELLUM_ATTRIBUTE_EXPORTER = 'castellum.recruitment.attribute_exporters.JSONExporter'

SCHEDULER_URL = ''
SCHEDULER_TOKEN = ''
