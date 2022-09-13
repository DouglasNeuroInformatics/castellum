import datetime
import math

import castellum_pseudonyms
from dateutil.relativedelta import relativedelta

from .base import *
from .mail import *

ALLOWED_HOSTS = []

# Set this to True to prevent creating insecure demo content in production
PRODUCTION = False

CASTELLUM_SITE_TITLE = 'Castellum'

CASTELLUM_LOGOUT_TIMEOUT = datetime.timedelta(seconds=15 * 60)
SESSION_COOKIE_AGE = 24 * 60 * 60

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

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

# By default, Castellum does not serve media (aka "uploaded") files.
# You have 3 options here:
#
# - Set PROTECTED_MEDIA_SERVER to "django" (only for development)
# - Set PROTECTED_MEDIA_SERVER to None and let a proxy serve the files
#   instead. This is insecure because it bypasses Castellum login.
# - Set PROTECTED_MEDIA_SERVER to the proxy server you use (e.g.
#   'nginx', 'uwsgi') to use X-Sendfile. You will have to configure
#   the proxy accordingly. This option is strongly recommended.
#
# references:
# - https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#django.contrib.staticfiles.views.serve
# - https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/
# - https://uwsgi-docs.readthedocs.io/en/latest/Snippets.html#x-sendfile-emulation
PROTECTED_MEDIA_SERVER = None
PROTECTED_MEDIA_URL = '/protected/'

# Two factor authentication
# See https://github.com/xi/django-mfa3
MFA_SITE_TITLE = 'Castellum'
MFA_DOMAIN = None


CASTELLUM_ENABLE_STUDY_EXPORT = True

# timespan a subject should be allowed to remain in the database without
# consent given
CASTELLUM_CONSENT_REVIEW_PERIOD = relativedelta(weeks=2)

# timespan a subject should be allowed to remain in the database
# after requesting to be deleted
CASTELLUM_SUBJECT_DELETION_PERIOD = datetime.timedelta(days=30)

CASTELLUM_APPOINTMENT_REMINDER_PERIOD = datetime.timedelta(days=3)

# the number of subjects that is added to the recruitment list every time
CASTELLUM_RECRUITMENT_BATCH_SIZE = 15

# Recruiters are not supposed to add excessive numbers of subjects to
# After reaching the hard limit, no more subjects can be added.
# max_number_of_subjects = study.min_subject_count * CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR
CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR = 2
CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT = math.inf

# Used to determine whether there are enough potential subjects to
# complete the study. If not, a warning is shown during filter creation.
CASTELLUM_EXPECTED_SUBJECT_FACTOR = 10

# recommended timespan between one contact attempt and another one from
# a different study recruitment
CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS = relativedelta(weeks=2)

# what is considered "has recently participated in a study"
CASTELLUM_RECENT_ACTIVITY_PERIOD = relativedelta(months=4)

# timespan after which uncontacted subjects with consent will show up in
# MaintenanceEstrangedSubjectsView
CASTELLUM_ENSTRANGED_SUBJECTS_PERIOD = relativedelta(months=18)

# default execution tags which are automatically created for each new study
CASTELLUM_DEFAULT_EXECUTION_TAGS = [
    ('ready', 'info'),
    ('done', 'success'),
    ('contact required', 'warning'),
]

# Email for announcing new GDPR requests
# make sure to setup a cron-job for ``notify_to_be_deleted``
CASTELLUM_GDPR_NOTIFICATION_TO = []

CASTELLUM_FILE_UPLOAD_MAX_SIZE = 5000000

# A function that generates a random pseudonym.
# (bits: int) -> str (maximum 64 chars)
# First argument is a hint about the number of random bits that should be included.
CASTELLUM_PSEUDONYM_GENERATE = castellum_pseudonyms.generate

# A function that raises a ValueError if the pseudonym's format is invalid.
#
# Returns a *cleaned* pseudonym. This can be used to implement
# auto-correction. But in most cases this will be the same as the input
# value.
#
# See also https://docs.djangoproject.com/en/stable/ref/forms/fields/#django.forms.Field.clean
CASTELLUM_PSEUDONYM_CLEAN = castellum_pseudonyms.clean

CASTELLUM_STUDY_DOMAIN_BITS = 20
CASTELLUM_SESSION_DOMAIN_BITS = 20

# If this is set, this attribute will automatically be filled from Contact.date_of_birth
CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID = None

CASTELLUM_FULL_AGE = 16

# Texts that apply to all studies
CASTELLUM_GENERAL_RECRUITMENT_TEXT = ''

# Default exporter used for attributes.
# Currently available options are
# - 'castellum.recruitment.attribute_exporters.JSONExporter'
# - 'castellum.recruitment.attribute_exporters.BIDSExporter'
# You can also implement your own if required.
# See castellum/recruitment/attribute_exporters.py for details
CASTELLUM_ATTRIBUTE_EXPORTER = 'castellum.recruitment.attribute_exporters.JSONExporter'

# Enables some additional views that expose content as JSON:
#
# list of studies
#   /studies/api/studies/?status=<edit|execution|finished>
# basic metadata of a study
#   /studies/api/studies/<study_id>/
# list of study domains:
#   /execution/api/studies/<study_id>/domains/
# list of pseudonyms in a domain:
#   /execution/api/studies/<study_id>/domains/<domain>/
# validate a single pseudonym
#   /execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/
# get exportable attributes:
#   /execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/attributes/
# resolve pseudonym to a target domain (can also be a general domain):
#   /execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/<target_domain>/
# get exportable attributes for general domains
#   /subjects/api/subjects/<domain>/<pseudonym>/attributes/
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

# Additional privacy levels for subjects.
#
# Each level is a tuple of a float value and a label.
# The effective level will be ``ceil(value)``.
# The values must be unique.
#
# This setting can be helpful if you want to distinguish different
# reasons for assigning a privacy level.
CASTELLUM_CUSTOM_PRIVACY_LEVELS = [
    # (0.5, '1 (slightly increased)'),
]

SCHEDULER_URL = ''
SCHEDULER_TOKEN = ''
