import datetime

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

# Secondary language in emails for readers who do not understand the
# primary language
CASTELLUM_FALLBACK_LANGUAGE = 'en'
CASTELLUM_FALLBACK_LANGUAGE_MARKERS = (
    '++++ FOR INFORMATION IN ENGLISH SEE BELOW ++++',
    '++++ INFORMATION IN ENGLISH ++++',
)

CASTELLUM_APPOINTMENT_REMINDER_PERIOD = datetime.timedelta(days=3)  # deprecated
CASTELLUM_APPOINTMENT_DEFAULT_FIRST_REMINDER_DAYS = 3
CASTELLUM_APPOINTMENT_DEFAULT_SECOND_REMINDER_DAYS = None
CASTELLUM_APPOINTMENT_MAIL_SUBJECT = "Reminder: You have an appointment"
CASTELLUM_APPOINTMENT_MAIL_BODY = (
    "Guten Tag {name},\n\n"
    "wir möchten Sie an Ihren Termin in der Studie {study} am {date} erinnern.\n\n"
    "Bitte informieren Sie uns so früh wie möglich, "
    "falls Sie Ihren Termin ändern oder absagen müssen. "
    "Unsere Experimente sind oft mit hohem Aufwand und Kosten verbunden. "
    "Wenn Sie wiederholt nicht zu Terminen erscheinen, "
    "können wir Sie für zukünftige Studien nicht mehr berücksichtigen.\n\n"
    "Für Rückfragen zu Ihrem Termin wenden Sie sich bitte an {reply_to}.\n\n"
    "Zusätzliche Informationen:\n"
    "{session_reminder_text}\n\n"
    "Mit freundlichen Grüßen\ndas Rekrutierungsteam"
)
CASTELLUM_APPOINTMENT_MAIL_BODY_EN = (
    "Dear {name},\n\n"
    "we would like to kindly remind you of your appointment in "
    "study {study} on {date}.\n\n"
    "If you have to change or cancel your appointment, please make sure to notify "
    "us as early as possible. Our experiments are often complex and expensive. If "
    "you do not show up for appointments repeatedly, we may no longer consider "
    "you for future studies.\n\n"
    "If you have any questions about your appointment, "
    "please get in touch with {reply_to}.\n\n"
    "Additional information:\n"
    "{session_reminder_text}\n\n"
    "Sincerely yours\nthe recruitment team"
)
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_SUBJECT = "Appointment reminders for {study}"
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY = (
    "The following subjects have upcoming appointments, but could not be reached by email. "
    "Please contact them by other means to remind them of their appointment:\n\n{urls}"
)
CASTELLUM_APPOINTMENT_NO_EMAIL_MAIL_BODY_EN = None

CASTELLUM_REMINDER_MAIL_SUBJECT_TEMPLATE = "Reminder/Erinnerung: {mail_subject}"

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
    'we received an export request from a subject who participated in {study}. Please gather all '
    'information related to the following subject:\n\n'
    '{url}\n(link only available for conductors)\n\n'
    'If you have any questions, feel free to get back to me.\n\n'
    '{sender_name}\n'
)
CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_BODY_EN = None

CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_SUBJECT = '[{study}] Deletion requested'
CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY = (
    'Dear {name},\n\n'
    'we received a deletion request from a subject who participated in {study}. Please delete all '
    'information related to the following subject:\n\n'
    '{url}\n(link only available for conductors)\n\n'
    'If you have any questions, feel free to get back to me.\n\n'
    '{sender_name}\n'
)
CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY_EN = None

CASTELLUM_SESSIONS_END_MAIL_SUBJECT = '[{study}] Sessions ended'
CASTELLUM_SESSIONS_END_MAIL_BODY = (
    'Please note that the data collection of study {study} ends today (according to the study '
    'settings in Castellum). Therefore, now would be a good time to verify again that all '
    'appointments and participations are correctly maintained in Castellum. If necessary, you '
    'can extend the data collection period in the study settings.\n\n'
    'Be aware that complete and correct tracking of participations in Castellum is essential '
    'as Castellum is the central starting point to carry out requests in respect to GDPR data '
    'subjects rights.'
)
CASTELLUM_SESSIONS_END_MAIL_BODY_EN = None

CASTELLUM_REPORT_NOTIFICATION_SUBJECT = 'Subject reported'
CASTELLUM_REPORT_NOTIFICATION_BODY = (
    'A user reported a subject for inappropriate behavior. '
    'Please review the report here:\n\n{url}'
)
CASTELLUM_REPORT_NOTIFICATION_BODY_EN = None
