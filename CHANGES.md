# 0.61.0 (2021-06-15)

## breaking changes

-   The system for reliability has been replaced. So far you could enter
    whether a subject has shown up for each individual appointment. With
    the new system, you only state whether you would invite this subject
    again for further studies.
-   Execution tags can no longer use the grey color. This is to avoid
    confusion with builtin badges.

## bug fixes

-   Fixed some cases in which the list of sessions was not in the
    correct order.

## new features

-   It is now possible to assign the responsibility for keeping contact
    with a participant to a recruiter or conductor respectively.
-   User tokens can now be changed in the admin UI. This is mostly
    useful to delete compromised tokens. User tokens are currently used
    for authentication with calendar feeds and may in the future be used
    for additional API endpoints.


# 0.60.0 (2021-05-25)

## bug fixes

-   In some cases studies were missing in the participation recruitment
    view in subject management if the subject already had a participation
    but was not participating.

## new features

-   Study approvers now have access to an overview of all the settings
    for a study. Any changes that were made since the study was started
    are highlighted.
-   In Execution, tags can now be assigned to subjects.
    The list of tags can be changed for each study individually.
    A set of default tags is created for each new study.
-   "Gender" is now an optional field for subjetcs. As a result, it no
    longer defaults to "female".
-   The dropout UI was expanded to include more information and allows
    to choose between drop out and keeping the data collected this far
    and drop out and deleting all data.


# 0.59.0 (2021-05-05)

## breaking changes

-   The `clearsessions` command should be used in place of
    `clear_session` (see security section for details)
-   The usernames of demo users (used for login) have been changed to
    lowercase, e.g. "vera" instead of "Vera".
-   The new command `notify_sessions_end` should be run in a daily cron
    job (see new features section for details)

## security

-   It is now possible to require authentication for uploaded files. We
    strongly recommend to use this option if possible. This usually
    requires some configuration on the proxy server. See the new setting
    `PROTECTED_MEDIA_SERVER` for details.
-   Users are now automatically logged out every night at midnight.
    Previously this was handled via the `clear_sessions` command (which
    was consequently removed). However, the `clearsessions` command
    should be used in its place to remove stale sessions from the
    database.

## new features

-   The execution area gained a new "progress" tab that shows pretty
    progress bars for participations and appointments.
-   It is now possible to provide translations for most internal mails.
-   The new command `notify_sessions_end` can be used to send useful
    information to coordinators and conductors at the end of studies.


# 0.58.1 (2021-04-14)

## bug fixes

-   Study conductors are informed via mail when an upcoming appointment
    is changed on short notice. In some cases the current date was
    included in place of a missing date.
-   "Announce status changes" for studies was not actually used.
-   Initial contact attempts after mail recruitment should be 1, not 0
    (regression from 0.56.0)


# 0.58.0 (2021-04-13)

## security

-   Update to Django 3.2. This is a long-term support release. It will
    receive security updates for at least three years.

## bug fixes

-   Icons in calendars were missing. This was a regression that was
    introduced in 0.57.0.

## new features

-   Participation status wording was refined:
    -   "invited" -> "participating"
    -   "unsuitable" -> "excluded"
-   The default value for appointment showup has been renamed from
    "showup" to "no issues".
-   So far each study had one pseudonym domain, i.e. one pseudonym per
    subject. Study coordinators can now create additional domains so
    subjects can have more than one pseudonym. (A pseudonym is only
    meaningful in combination with its domain, so if you use this
    feature make sure to document which domain is used where.)
-   Study conductors can now mark subjects as "excluded" (previously
    "unsuitable") when they drop out of a study. Before this was only
    possible for recruiters.
-   The number of invited and required subjects is now also displayed in
    execution.
-   If a subject has not shown up to an appointment, the appointment is
    no longer counted. This way it is easier to see that you need to
    reschedule. Such appointments are also highlighted in the execution
    calendar.
-   If any of your actions in castellum triggers an email to other
    users, you will now receive a copy of that email.
-   When a subject should be deleted from castellum, the data protection
    coordinator first needs to contact all studies in which the subject
    has participated. There is now a button to automatically generate
    emails with all required information to simplify that task.


# 0.57.0 (2021-03-23)

## breaking changes

-   It is now possible to edit study filters after the study has already
    been started. The previous restriction proved to be ineffective
    while adding annoyances for users.

## bug fixes

-   Fixed formatting of attribute completeness (rounded percentage).
    This was a regression that was introduced in 0.56.0.
-   The recruitment consent checkbox is now disabled (instead of simply
    doing nothing) if javascript fails to run.

## new features

-   The recruitment cleanup introduced in 0.52.0 has been overhauled. It
    was simplified considerably by taking away some rarely used options.
    It also gained a new option to cleanup subjects that do not match
    the study filters which should be especially useful if filters
    change during recruitment.
-   The select2 library is now used to render some select boxes,
    most notably excluded studies and study tags. This has an overall
    better usability, especially if there are many options. Notable
    features include search and autocompletion.
-   Because we still receive many bug reports related to Internet
    Explorer there is now a warning message explaining the lack of
    support for that browser specifically.


# 0.56.0 (2021-03-02)

## breaking changes

-   The migrations that have been squashed in 0.53.0 have been removed.
    If you are using a version before 0.53.0 you must update to 0.53.0
    before you can update to this version.

## bug fixes

-   The session reminder text introduced in 0.54.0 is now copied
    when duplicating a study.
-   Fixed a crash in followup ICS feeds that use a followup time.

## new features

-   The "add to study" tab in subject management has been completely
    overhauled. Principal subject managers can now bypass recruitment
    completely. This is especially helpful for organisations that do
    not intend to use castellum for recruitment.
-   It is now possible to send a single reminder for each recruitment
    mail batch.
-   Session management has been moved to its own tab because it is
    not necessarily related to recruitment.
-   Session management now includes a link to the scheduler (if that
    feature is enabled)
-   The maintenance dashboard now includes a tab for migrating away from
    subject notes which have been deprecated in 0.53.0.
-   House numbers can now have up to 16 characters.
-   Schedule IDs can now be strings and have up to 64 characters.


# 0.55.1 (2021-02-15)

## security

-   Fix leak of subject slug in recruitment. This is not an issue on its
    own, but could lead to more serious leaks if combined with other
    vulnerabilities.


# 0.55.0 (2021-02-09)

## breaking changes

-   The default logging configuration has been removed, so now the
    [defaults set by django](https://docs.djangoproject.com/en/3.1/topics/logging/#django-s-default-logging-configuration)
    are used. See `docs/example_deployment/settings.py` for an example
    that replicates the old behavior.

## new features

-   Recruitment/Execution contacting details provide hint that the
    current guardian may have more wards who could be invited.
-   Exclude underage subjects with incomplete attributes from
    maintenance dashboard as attribute completion may not be possible
    for these subjects


# 0.54.2 (2021-02-01)

## security

-   Update to Django 3.1.6
-   Restrict cookies to secure connections by default
-   The number of booked appointments was multiplied by the total
    number of participations for a subject. This allowed unauthorized
    users to infer that number.

## bug fixes

-   Fix some cases where blocked subjects were not handled correctly.
    Notably blocking is now considered a legal basis in the data
    protection dashboard.
-   Fix the number of booked appointments in the recruitment and
    execution lists.


# 0.54.1 (2021-01-20)

## bug fixes

-   Off-by-one error in age statistics


# 0.54.0 (2021-01-19)

## security

-   Default security settings have been enhanced to prevent some kinds
    of unnecessary access to cookies.

## new features

-   Sessions can now provide a text that is included in appointment
    reminder mails. You may need to adapt
    `CASTELLUM_APPOINTMENT_MAIL_BODY` to include the new field.
-   All links to calendar feeds have been extracted from the UI and
    collected in a single view at `/feeds/`.
-   Age statistics in recruitment now use special groupings if study
    filters only allow subjects under the age of 2/18 years.
-   Mails that are sent to more than one recipient (i.e. guardians) do
    not contain the other recipients in the `To` or `Cc` header for
    privacy reasons. However, starting from this release, the names of
    all recipients are included in the mail body. The text that is used
    can be customized using the `recipients_text` field within the
    `CASTELLUM_MAIL` setting.
-   `CASTELLUM_DATE_OF_BIRTH_ATTRIBUTE_ID` (default: empty) allows to
    specify an attribute that will automatically be filled from
    `Contact.date_of_birth`. Before it was quite common that users had
    to enter the date of birth twice.
-   It is now possible to block a subject due to inappropriate behavior.
    Blocking is considered a sufficient legal basis of its own,
    according to Art. 6 (1) lit. f GDPR.

## bug fixes

-   When adding guardians to a subject, newly created guardians were not
    added properly.


# 0.53.0 (release skipped)

## deprecations

-   It turned out that subject notes were not used, at least not as
    intended. So as of this release they are deprecated. It is no longer
    possible to enter new notes. Existing notes should be migrated to
    more suitable features, e.g. availability, study type disinterest,
    or study participation.
-   Some existing migrations have been been squashed and will be removed
    in a future release.

## new features

-   `CASTELLUM_GENERAL_RECRUITMENT_TEXT` allows to enter a recruitment
    text that will be used for all studies (default: empty).
-   `CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT` allows to set a weekly per
    study limit on mail recruitment (default: infinity).
-   Allow to send test mails to own email address for preview.

## bug fixes

-   `onetime_invitation_disinterest` and `study_type_disinterest` were
    missing from the subject export.
-   Fixed a 500 response when saving study recruitment settings.
-   Fixed a 500 response when trying to resolve an invalid pseudonym.


# 0.52.0 (2020-12-01)

## new features

-   It is now possible to find subjects by their phone number.
-   The recruitment list now has a "cleanup" button that can be used to
    automatically mark several subjects as "unsuitable". We hope this is
    useful e.g. for unresponsive subjects during mail recruitment.
-   The number of booked appointments is now shown in the list (in both
    recruitment and execution) so you can easily find subjects that
    don't have an appointment yet.
-   It is now possible to export pseudonyms and attributes for
    participants from the execution list. The format can be configured
    using the new `CASTELLUM_ATTRIBUTE_EXPORTER` setting.
-   The UI to setup study sessions has been changed. No new features
    have been added yet, but the new structure should make it easier to
    add more features in the future.
-   In recruitment, saving changes to a subject no longer sends you back
    to the list automatically. Instead, there is an explicit button to
    go back.
