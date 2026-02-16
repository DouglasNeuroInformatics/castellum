import datetime
import math

import castellum_pseudonyms
from dateutil.relativedelta import relativedelta

from .base import *

ALLOWED_HOSTS = []

# Set this to True to prevent the creation of insecure demo content
PRODUCTION = False

CASTELLUM_SITE_TITLE = 'Castellum'

# Optional logo
#
# The logo will be displayed next to the title as a 40x40 square.
# The logo most be available from the same origin.
# All other origins are blocked for security reasons.
#
# Example: '/static/my_logo.svg'
CASTELLUM_SITE_LOGO = None

# You can overwrite the primary color and its two darker shades.
# Default: ['#0d6efd', '#0b5ed7', '#0a58ca']
BOOTSTRAP_THEME_COLORS = None

# Will be included on the front page
# Set to `None` to disable
CASTELLUM_DOCUMENTATION_LINK = 'https://castellum.mpib.berlin/castellum/docs/'

CASTELLUM_LOGOUT_TIMEOUT = relativedelta(minutes=15)
SESSION_COOKIE_AGE = 24 * 60 * 60

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True

# Internationalization
LANGUAGE_CODE = 'en'
CASTELLUM_LANGUAGES = ['de', 'en']
TIME_ZONE = 'Europe/Berlin'
PHONENUMBER_DEFAULT_REGION = 'DE'

# By default, Castellum does not serve media (aka "uploaded") files.
# You have 2 options here:
#
# - Set PROTECTED_MEDIA_SERVER to "django" (only for development)
# - Set PROTECTED_MEDIA_SERVER to the proxy server you use (e.g.
#   'nginx', 'uwsgi') to use X-Sendfile. You will have to configure
#   the proxy accordingly. This option is strongly recommended.
#
# references:
# - https://docs.djangoproject.com/en/3.2/ref/contrib/staticfiles/#django.contrib.staticfiles.views.serve
# - https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/
# - https://uwsgi-docs.readthedocs.io/en/latest/Snippets.html#x-sendfile-emulation
PROTECTED_MEDIA_SERVER = 'nginx'
PROTECTED_MEDIA_URL = '/protected/'

# Two factor authentication
# See https://github.com/xi/django-mfa3
MFA_SITE_TITLE = 'Castellum'
MFA_DOMAIN = 'localhost'

# Add additional metadata fields to studies
CASTELLUM_ENABLE_STUDY_METADATA = [
    'principal_investigator',
    'affiliated_scientists',
    'affiliated_research_assistants',
    'description',
    'url',
]

# timespan a subject should be allowed to remain in the database without
# consent given
CASTELLUM_CONSENT_REVIEW_PERIOD = relativedelta(weeks=2)

# timespan a subject should be allowed to remain in the database
# after requesting to be deleted
CASTELLUM_SUBJECT_DELETION_PERIOD = datetime.timedelta(days=30)

# timespan after the last update to a study that interest in study news
# should count as a legal basis
CASTELLUM_STUDY_NEWS_PERIOD = relativedelta(years=3)

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

# Studies can filter for recent activity by date. Malicious study
# coordinators could try to identify a specific subject by filtering on
# that specific date. As a counter measure, you can set a minimum
# timespan for recent activity filters.
CASTELLUM_MINIMUM_ACTIVITY_PERIOD = datetime.timedelta(days=14)

# timespan after which uncontacted subjects with consent will show up in
# MaintenanceEstrangedSubjectsView
CASTELLUM_ENSTRANGED_SUBJECTS_PERIOD = relativedelta(months=18)

# default execution tags which are automatically created for each new study
# CASTELLUM_DEFAULT_EXECUTION_TAGS = [
#     ('ready', 'info'),
#     ('done', 'success'),
#     ('contact required', 'warning'),
# ]
CASTELLUM_DEFAULT_EXECUTION_TAGS = []

# Email for announcing new GDPR requests
# make sure to setup a cron-job for ``notify_to_be_deleted``
CASTELLUM_GDPR_NOTIFICATION_TO = []

# Emails that should receive a notification when a subject is reported
# for inappropriate behavior.
#
# The recipients need the ``subjects.view_report`` permission to
# actually access the report.
CASTELLUM_REPORT_NOTIFICATION_TO = []

# Emails that should be CCed when a study is notified of some deadline.
# This could be someone who keeps an overview of all studies at an organization.
CASTELLUM_STUDY_END_NOTIFICATION_CC = []

# Text that is shown to users who file a report.
#
# You can include details about the review process or links for specific
# support offerings.
CASTELLUM_REPORT_TEXT = (
    'If you experience inappropriate behavior from a subject, please file a report so '
    'we can make sure that this subject will never be invited again.'
)

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

# Enables SSH key management for crypto shredding:
#
# get or create SSH public key:
#   GET /execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/ssh-key/
# delete private key (crypto shred):
#   DELETE /execution/api/studies/<study_id>/domains/<domain>/<pseudonym>/ssh-key/
CASTELLUM_SSH_KEYS_ENABLED = False

# By default, only a small set of models is included in the admin UI (`/admin/`).
#
# This setting allows you to include all models in the admin UI.
CASTELLUM_ADVANCED_ADMIN_UI = False

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

# By default, the monitoring log records all subject searches. This
# allows you to detect users who abuse this feature, e.g. to search for
# famous people.
#
# On the other hand, the search text usually contains personal
# information such as names and email addresses. It depends on your
# specific threat model whether you want to include this or not.
CASTELLUM_MONITORING_INCLUDE_SEARCH = True

# Create an audit trail
#
# This audit is intentionally very limited: Neither the before nor the after values are
# stored. Only who did what when.
#
# Users can see the audit events related to subjects or studies if they have the
# `subjects.view_audit_trail` / `studies.view_audit_trail` permission. The full list of
# events is also available in the admin UI.
#
# Events are automatically deleted after one year.
CASTELLUM_AUDIT_TRAIL_ENABLED = False

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

# See https://git.mpib-berlin.mpg.de/castellum/castellum_scheduler
SCHEDULER_URL = ''
SCHEDULER_TOKEN = ''

# settings for sending mails (defaults to general settings)
# Complete example:
# {
#     'from_email': 'Castellum <castellum@example.com>',
#     'language': 'en',
#     'subject_prefix': '[Castellum] ',
#     'recipients_text': '\n\nThis email was sent to: {}',
#     'signature': '\n\n-- \nAutomatically sent by Castellum',
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

# Base URL that is used when sending emails from cron jobs, e.g. "https://example.com"
CASTELLUM_EMAIL_BASE_URL = None

# Secondary language in emails for readers who do not understand the
# primary language
CASTELLUM_FALLBACK_LANGUAGE = 'en'
CASTELLUM_FALLBACK_LANGUAGE_MARKERS = (
    '++++ FOR INFORMATION IN ENGLISH SEE BELOW ++++',
    '++++ INFORMATION IN ENGLISH ++++',
)

CASTELLUM_APPOINTMENT_DEFAULT_FIRST_REMINDER_DAYS = 3
CASTELLUM_APPOINTMENT_DEFAULT_SECOND_REMINDER_DAYS = None
CASTELLUM_APPOINTMENT_MAIL_SUBJECT = 'Reminder: You have an appointment'
CASTELLUM_APPOINTMENT_MAIL_BODY = (
    'Guten Tag {name},\n\n'
    'wir möchten Sie an Ihren Termin in der Studie {study} am {date} erinnern.\n\n'
    'Bitte informieren Sie uns so früh wie möglich, '
    'falls Sie Ihren Termin ändern oder absagen müssen. '
    'Unsere Experimente sind oft mit hohem Aufwand und Kosten verbunden. '
    'Wenn Sie wiederholt nicht zu Terminen erscheinen, '
    'können wir Sie für zukünftige Studien nicht mehr berücksichtigen.\n\n'
    'Für Rückfragen zu Ihrem Termin wenden Sie sich bitte an {reply_to}.\n\n'
    'Zusätzliche Informationen:\n'
    '{session_reminder_text}\n\n'
    'Mit freundlichen Grüßen\ndas Rekrutierungsteam'
)
CASTELLUM_APPOINTMENT_MAIL_BODY_EN = (
    'Dear {name},\n\n'
    'we would like to kindly remind you of your appointment in '
    'study {study} on {date}.\n\n'
    'If you have to change or cancel your appointment, please make sure to notify '
    'us as early as possible. Our experiments are often complex and expensive. If '
    'you do not show up for appointments repeatedly, we may no longer consider '
    'you for future studies.\n\n'
    'If you have any questions about your appointment, '
    'please get in touch with {reply_to}.\n\n'
    'Additional information:\n'
    '{session_reminder_text}\n\n'
    'Sincerely yours\nthe recruitment team'
)
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_SUBJECT = 'Appointment reminders for {study}'
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY = (
    'The following subjects have upcoming appointments, but could not be reached by '
    'email. Please contact them by other means to remind them of their appointment:\n\n'
    '{urls}'
)
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY_EN = None

CASTELLUM_REMINDER_MAIL_SUBJECT_TEMPLATE = 'Reminder/Erinnerung: {mail_subject}'

CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_SUBJECT = 'Subject export'
CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY = (
    'The following subject should be exported: {url}'
)
CASTELLUM_EXPORT_SUBJECT_NOTIFICATION_BODY_EN = None
CASTELLUM_DELETE_SUBJECT_NOTIFICATION_SUBJECT = 'Subject deletion'
CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY = (
    'The following subject should be deleted: {url}'
)
CASTELLUM_DELETE_SUBJECT_NOTIFICATION_BODY_EN = None

CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_SUBJECT = 'Upcoming appointment changed'
CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY = """
An upcoming appointment for a participant in the study "{study}" has changed:

{change}

Participant details: {participation_url}
Study calendar: {calendar_url}
"""
CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY_EN = None

CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_SUBJECT = '[{study}] Export requested'
CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_BODY = (
    'Dear {name},\n\n'
    'we received an export request from a subject who participated in {study}. '
    'Please gather all information related to the following subject:\n\n'
    '{url}\n(link only available for conductors)\n\n'
    'If you have any questions, feel free to get back to me.\n\n'
    '{sender_name}\n'
)
CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_BODY_EN = None

CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_SUBJECT = '[{study}] Deletion requested'
CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY = (
    'Dear {name},\n\n'
    'we received a deletion request from a subject who participated in {study}. '
    'Please delete all information related to the following subject:\n\n'
    '{url}\n(link only available for conductors)\n\n'
    'If you have any questions, feel free to get back to me.\n\n'
    '{sender_name}\n'
)
CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY_EN = None

CASTELLUM_SESSIONS_END_MAIL_SUBJECT = '[{study}] End of data collection'
CASTELLUM_SESSIONS_END_MAIL_BODY = (
    'This is a reminder that, according to the information you entered in '
    'Castellum, the data collection for study "{study}" ends today: '
    '{study_url}\n\n'
    'Please mark the study as finished or adapt the end date in Castellum '
    'if the data collection has been extended. You will still be able to '
    'resume the study afterwards.\n\n'
    'Remember that correct and complete tracking of this information is '
    'neccessary so we can responsibly handle the personal data of the study '
    'participants and delete the data when it is no longer needed.'
)
CASTELLUM_SESSIONS_END_MAIL_BODY_EN = None

CASTELLUM_PSEUDONYMS_DELETE_MAIL_SUBJECT = '[{study}] Pseudonyms should be deleted'
CASTELLUM_PSEUDONYMS_DELETE_MAIL_BODY = (
    'This is a reminder that, according to the information you entered in '
    'Castellum, the pseudonyms for study "{study}" should be '
    'deleted today: {study_url}\n\n'
    'Please make sure that all data has been anonymized and then delete the '
    'pseudonym lists from Castellum.\n\n'
    'Remember that correct and complete tracking of this information is '
    'neccessary so we can responsibly handle the personal data of the study '
    'participants and delete the data when it is no longer needed.'
)
CASTELLUM_PSEUDONYMS_DELETE_MAIL_BODY_EN = None

CASTELLUM_REPORT_NOTIFICATION_SUBJECT = 'Subject reported'
CASTELLUM_REPORT_NOTIFICATION_BODY = (
    'A user reported a subject for inappropriate behavior. '
    'Please review the report here:\n\n{url}'
)
CASTELLUM_REPORT_NOTIFICATION_BODY_EN = None

# used by the notify_on_full_age command
CASTELLUM_FULL_AGE_MAIL_SUBJECT = None
CASTELLUM_FULL_AGE_MAIL_BODY = None

# used by the notify_on_consent_expire command
CASTELLUM_CONSENT_EXPIRE_AT_WARN_BEFORE = relativedelta(weeks=2)
CASTELLUM_CONSENT_EXPIRE_AT_MAIL_TO = []
CASTELLUM_CONSENT_EXPIRE_AT_MAIL_SUBJECT = 'Consents about to expire'
CASTELLUM_CONSENT_EXPIRE_AT_MAIL_BODY = (
    'Some recruitment consents will expire soon:\n\n{subject_urls}'
)

# Statistics that should be displayed on the subject search view
#
# Each entry must be a callable (or a string identifying a callable) that
# returns ``(label: str, count: int)``.
# Ideally, the label should be translatable.
#
# Example::
#
#     def get_right_handed():
#         from castellum.subjects.stats import get_attribute_filter
#         return get_attribute_filter(1, 'exact', 1)
CASTELLUM_SUBJECT_STATS = [
    'castellum.subjects.stats.get_contact_updated',
    'castellum.subjects.stats.get_attributes_complete',
    'castellum.subjects.stats.get_participated_in_study',
    'castellum.subjects.stats.get_recruitable',
]

# Grouping used for age statistics
CASTELLUM_AGE_BUCKETS = [
    (17, '<18'),
    (25, '18-25'),
    (30, '26-30'),
    (35, '31-35'),
    (40, '36-40'),
    (45, '41-45'),
    (50, '46-50'),
    (55, '51-55'),
    (60, '56-60'),
    (65, '61-65'),
    (70, '66-70'),
    (math.inf, '>70'),
]
