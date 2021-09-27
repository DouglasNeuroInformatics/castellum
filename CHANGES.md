# 0.66.0 (unreleased)

## security

-   Fixed a missing permission check that allowed subject managers to
    see and edit data of subjects in recruitment without needing to be
    recruiters.
-   Fixed a missing check that allowed users to add legal
    representatives to a subject without checking the representative's
    privacy level.
-   Fixed leak of subject ID in recruitment and execution. This is not
    an issue on its own, but could lead to more serious leaks if
    combined with other vulnerabilities.

## breaking changes

-   Removed timeslot-based availability. This includes the `timeslots`
    fixture.
-   Renamed the command `delete_filter_trials` to
    `cleanup_filter_trials`.
-   Removed the optional argument `--limit` from the command
    `notify_to_be_deleted`.
-   The new command `cleanup_availability` to clear "not available
    until" entries that have passed. It should be run daily.
-   Adding and removing legal representatives now requires the global
    `subjects.change_subject` permission.

## new features

-   Changed "guardian" to "legal representative"
-   It is now possible to edit contact data of legal representatives in
    recruitment and execution.
-   Contact details now also display "not available until" if the
    subject has legal representatives.
-   Contact details now display whether a legal representative is
    blocked or deceased.
-   Command logs are now more verbose


# 0.65.2 (2021-09-10)

## bug fixes

-   Fixed timezone offset in some places, most importantly in
    appointment reminder mails.


# 0.65.1 (2021-09-08)

## bug fixes

-   Fixed crash in filter trials due to non-unique study names.


# 0.65.0 (2021-09-07)

## security

-   Due to insufficient validation, users were able to add filters to
    other studies.

## breaking changes

-   `CASTELLUM_DELETE_NOTIFICATION_TO` was renamed to
    `CASTELLUM_GDPR_NOTIFICATION_TO` and now takes a list of email
    addresses instead of a single one.
-   `castellum.recruitment.attribute_exporters.JSONExporter` now
    includes unknown attributes with a value of `null` instead of
    skipping them.

## bug fixes

-   fix a crash in GDPR export if `CASTELLUM_GDPR_NOTIFICATION_TO` is
    set

## new features

-   There is now an API to interact with pseudonyms. See `docs/API.md`
    for details.
-   PR mails are now only sent once per study and include the
    recruitment mail body instead of the full recruitment text (if
    available).
-   Two factor authentication now provides recovery codes. The set of
    enabled authentication methods can be controlled with the
    `MFA_METHODS` setting.
-   It is now possible to select exportable attributes regardless of
    privacy level.
-   Study conductors with an insufficient privacy level are now longer
    allowed to export attributes. Previously they were allowed to do it,
    but the export was incomplete.


# 0.64.0 (2021-08-17)

## breaking changes

-   Names of studies now have to be unique. Existing non-unique names
    are automatically changed by appending a number.
-   django-auth-ldap (included in the castellum docker image) has been
    updated to [3.0.0](https://django-auth-ldap.readthedocs.io/en/latest/changes.html)
-   Hardcoded subject notes (deprecated since 0.53.0) have been removed

## bug fixes

-   When duplicating a study, its domains are now also duplicated.
-   In subject search, characters with diacritics are no longer ignored.
    For example, "Gerçeği" is now treated the same as "Gercegi", not
    "Gerei".
-   Subject notes have been deprecated and read-only since 0.53.0. This
    version restores an option to delete them to aid migration to other
    mechanisms.

## new features

-   For data that is not directly related to a specific study there are
    now [general pseudonym domains](https://castellum.mpib.berlin/documentation/en/privacy.html#using-pseudonyms-from-general-domains)
-   Access to pseudonyms is now included in the monitoring log. In the
    UI, pseudonyms therefore now have to be requested individually and
    are no longer shown all at once.
-   The UI for study pseudonyms has been changed so that it is now easy
    to access the domain key. The domain key is important to make sure
    that pseudonyms are unambiguous.
-   The form field used for multiple choice Attributes now uses select2
-   You are now asked for confirmation before sending mail recruitment
    reminders
-   (german translation) "Vormund" has been changed to "gesetzliche
    Vertreter\*in"


# 0.63.1 (2021-08-10)

## bug fixes

-   Fixed an error when using attribute export with MultipleChoiceField
-   Fixed multiple issues in the conditions for showing the
    "Appointments" and "Update data" tabs in both recruitment and
    execution


# 0.63.0 (2021-07-27)

## breaking changes

-   The new command `delete_filter_trials` should be executed daily

## bug fixes

-   In the recruitment list, the text "recently contacted in another
    recruitment" replaced other, potentially important information. It
    has been redesigned to be shown in addition to, not instead of, that
    information.
-   Removed an accidental loop through all subjects that made the
    contact form slow
-   Fixed crashes for subjects with unknown attributes
-   Fixed a warning about appointments outside of the planned time
    period
-   Do not display "unreachable" warning for subjects whose guardians
    are hidden due to privacy level
-   Clear followup time on participation status change

## new features

-   Study managers can now try filters without creating a complete
    study. The ephemeral "filter trial" studies that are created for
    this can be cleaned up using the `delete_filter_trials` command.
-   The navigation in recruitment and execution has been restructured.
-   Show * for required fields in relevant forms
-   Gender and date of birth are no longer required in contact form
-   Subjects can now be invited to a study even if exclusion criteria
    have not been checked.
-   Allow to search for subject slugs in admin UI


# 0.62.1 (2021-07-07)

## security

-   Do not allow users to see/delete other user's two factor
    authentication keys.


# 0.62.0 (2021-07-06)

## breaking changes

-   The new setting `MFA_DOMAIN` needs to be set to the domain of your
    actual server. See the entry on two factor authentication below for
    more information.

## bug fixes

-   Validation errors in the "create" tab in subject search were hidden
    because the "matches" tab was displayed by default. Now, if any tab
    contains an error message, it is displayed automatically.
-   Form validation sometimes resulted in 500 error pages instead of
    showing the validation errors. For example, this happened when a
    user submitted the recruitment form with an invalid participation
    status.

## new features

-   Users can now register a second factor for authentication. FIDO2 and
    TOTP are supported. Optionally you can enforce the use of two factor
    authentication for all users by adding
    `mfa.middleware.MFAEnforceMiddleware`. See
    [django-mfa3](https://github.com/xi/django-mfa3) for details.
-   A new "excluded by cleanup" badge is now displayed in recruitment to
    discern subjects who have been automatically excluded. This helps
    deciding which subjects can be recontacted if the need arises.
-   The appointment UI now explains when reminders will be sent out.
-   Attributes are now called "recruitment attributes" throughout the UI
    to clearly express the intended use.
-   The UI for selecting a tag color was simplified.
-   Study pseudonyms are now directly accessible from subject export.
    This facilitates the gathering of subject data from studies.
    The UI mirrors the way studies can be interacted with from subject
    deletion.


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
-   "Gender" is now an optional field for subjects. As a result, it no
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
