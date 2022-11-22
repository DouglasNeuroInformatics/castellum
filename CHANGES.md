# 0.84.0 (unrelease)

## new features

-   Allow to upload signed study consents


# 0.83.0 (2022-11-01)

## breaking changes

-   In the docker image, the `/log/` and `/media/` volumes have been
    moved to `/code/log/` and `/code/media/` respectively. This is to
    avoid conflicts as `/media/` is used as a mountpoint for removable
    media in many linux distributions.

## new features

-   The new setting `CASTELLUM_SITE_LOGO` can be used to add a logo to
    the header.
-   The new setting `BOOTSTRAP_THEME_COLORS` can be used to change the
    primary color.
-   The Admin UI to manage users has been improved. Among other things,
    it is now possible to add a description to each user, e.g. to
    reference their organisational unit.


# 0.82.1 (2022-10-11)

## bug fixes

-   Add missing translations
-   Handle exceptions when trying to send mails
-   Do not notify about all to be deleted subjects every time


# 0.82.0 (2022-09-20)

## breaking changes

-   The server-side validation of uploaded files was buggy and therefore
    removed.
-   It is no longer possible to document that additional suitability
    documents exist.

## bug fixes

-   The order of consent documents has been fixed

## new features

-   The new setting `CASTELLUM_SITE_TITLE` allows to change the site
    title
-   The way privacy levels are displayed has been redesigned. It should
    now be easier to tell if other users are able to access a subject or
    not.
-   Study type disinterest has been rephrased to also cover permanently
    unsuitable subjects.


# 0.81.0 (2022-08-30)

## breaking changes

-   Starting with this release, we will slightly change our release
    schedule. Feature releases will be less frequent. However, we still
    expect there to be a release every 3 weeks for dependency updates.
-   The docker image is now based on alpine linux 3.16
-   The temporary mechanism to honor recruitment consent grace periods
    introduced in 0.79.0 has been removed again.
-   The option `CASTELLUM_COVERLETTER_TEMPLATE` has been removed
-   The option for study reviewers to display a complete overview of the
    study has been removed. All actions concerning members and their
    permissions are instead logged to the monitoring log.
-   Date inputs now have a minimum value of 1900-01-01. This is to
    prevent typos.

## bug fixes

-   Fixed dates in the "waiting for consent" maintenance view

## new features

-   It is now possible to find subjects by their pseudonyms from general
    domains
-   Users are informed more prominently if a subject's data is
    incomplete.
-   Recruiters can now exclude a subject from a study even if they do
    not have the required privacy level.
-   The help texts for legal bases now provides a brief summary for each
    referenced legal article
-   The command `geocode_all` now returns an error if nominatim is not
    configured.
-   The development documentation has been restructured.
-   The docker image now includes a default uwsgi.ini
-   Study members are now included in the study export. We expect to do
    a bigger overhaul of the study export in the near future, so don't
    expect this to be stable.


# 0.80.1 (2022-08-22)

## bug fixes

-   Fix background color of execution tags (was white on white)


# 0.80.0 (2022-08-09)

## breaking changes

-   Subject notes have been removed. They have been deprecated since
    0.53.0.
-   The option to create a study as an "anonymous invitation" has been
    removed. Existing anonymous invitation will be deleted. If you want
    to keep them, you can remove the `is_anonymous_invitation` flag via
    the admin UI before doing the update.
-   The reception tile on the start page as well as the "Receptionist"
    user group have been removed.

## bug fixes

-   It is no longer possible to create subjects, subject creation
    requests, or contact creation requests via the admin UI because that
    could lead to inconsistent data.
-   The technical creation date of a consent document is no longer
    displayed because it does not necessarily correspond to the date
    when the real-world document was introduced.

## new features

-   Bootstrap has been updated to 5.2, so the UI got a slight refresh.
-   The recruitment list can now be filtered by "assigned to me".
-   When a subject that requested deletion is deleted, the date of the
    request is now included in the monitoring log.


# 0.79.0 (2022-07-19)

This release removes many rarely used features and brings a major
overhaul of the recruitment consent feature.

## breaking changes

-   The official contact email for this project has changed to
    <castellum@mpib-berlin.mpg.de>.
-   Exclusion criteria have been merged into recruitment texts. A
    study's exclusion criteria will automatically be appended to the
    recruitment text on migration. The contents of
    `CASTELLUM_GENERAL_EXCLUSION_CRITERIA` should similarily be appended
    to `CASTELLUM_GENERAL_RECRUITMENT_TEXT`.
-   `CASTELLUM_RECRUITMENT_SOFT_LIMIT` is no longer used.
-   The option to announce study status changes has been removed.
    Consequently, the settings `CASTELLUM_STUDY_STATUS_NOTIFICATION_TO`,
    `CASTELLUM_STUDY_STATUS_NOTIFICATION_SUBJECT`,
    `CASTELLUM_STUDY_STATUS_NOTIFICATION_BODY`, and
    `CASTELLUM_STUDY_STATUS_NOTIFICATION_BODY_EN` are no longer used.
-   The option to set a preferred contact method for subjects has been
    removed.
-   The option to import and export attribute descriptions has been
    removed.
-   The option to set privacy levels for attributes has been removed.
-   The script `create_attribute_descriptions` has been replaced by
    `loaddata attribute_descriptions`.
-   It is no longer possible to mark recruitment consent as "waiting for
    confirmation". Previously, castellum treated such a consent as a
    legal basis for a grace period (see
    `CASTELLUM_CONSENT_REVIEW_PERIOD`). Castellum now still uses
    `CASTELLUM_CONSENT_REVIEW_PERIOD` when a subject is newly created.
    It also provides a temporary mechanism to honor grace periods that
    were in effect during migration. You need to define organizational
    processes for the case when you are waiting for an updated consent
    while an old one is still in effect.

## new features

-   Recruitment consents have been redesigned from the ground up
    -   It is now possible to upload signed consent documents.
    -   It is now possible to explicitly select the consent document for
        a recruitment consent.
    -   It is now possible to manually select a name for a consent
        document (other than "Version X").
    -   It is no longer necessary to confirm the consent in a second
        step.
-   A subject's reliability is displayed less prominently


# 0.78.0 (2022-06-28)

## breaking changes

-   It is no longer possible to mark consent documents as invalid. They
    should be removed instead.

## bug fixes

-   When duplicating a study, the colors for execution tags are now
    copied correctly.
-   When duplicating a study, the study consent is no longer duplicated.
    This was also never really useful because the study consent is
    always specific to that study.

## new features

-   Uploaded files now have permission checks. For example, only members
    of a study can access the uploaded files for that study.
-   The study consent upload has been moved to a separate tab.
-   It is now possible to use feature collections in geofilters. This
    allows to use files e.g. from geojson.io without further
    modification.
-   Added admin UI for geolocations.
-   There is now a "pseudonyms deleted" badge in subject deletion that
    helps data protection coordinators to understand what is left to be
    done.
-   Privacy levels (both for subjects and attributes) are now included
    in attribute export and the corresponding API endpoints.
-   Added a marker for the minimum subject count to study progress bars.


# 0.77.0 (release skipped)


# 0.76.0 (release skipped)


# 0.75.1 (2022-05-10)

-   Fixed default value for subject's privacy level


# 0.75.0 (2022-04-26)

## bug fixes

-   Fixed showing the consent document in consent forms outside of
    subject management.

## new features

-   Broadcast messages allow to communicate important information to all
    users, e.g. scheduled maintenance.
-   The data protection dashboard now shows a new category ("unnecessary
    recruitment data") for subjects who have recruitment data, but no
    recruitment consent.
-   When editing an appointment, users can now select whether other
    users should be informed via mail or not.
-   The third cleanup option ("mismatch") now also excludes subjects
    without recruitment consent.
-   The new command `cleanup_dashboards` allows to delete all subjects
    listed in the data protection dashboard.
-   When deleting all pseudonym domains and a subject is also not
    interested in study news, a participation is no longer counted as
    legal basis to keep the subject's data
-   More precise wording in the subject deletion process to reflect that
    legally binding retention periods may prevent the deletion of
    scientific data even if this goes against the subject's wishes.


# 0.74.0 (2022-04-05)

## bug fixes

-   Fixed missing entries in reliability maintenance dashboard
-   Fixed autocompletion for the source field on subjects
-   Do not list blocked and deceased subjects in maintenance dashboards
-   Fixed wrong date in notification mail when an appointment is removed
-   Fixed order of sessions in appointment form

## breaking changes

-   It is no longer possible to assign conductors to participations.
    This feature has been replaced by appointment assignments (see
    below). Existing assignments are migrated automatically.
-   The default values for `CASTELLUM_SUBJECT_DELETE_STUDY_MAIL_BODY`
    and `CASTELLUM_SUBJECT_EXPORT_STUDY_MAIL_BODY` have been expanded
    with "(link only available for conductors)". If you have customized
    these settings you might want to adapt them.
-   `CASTELLUM_APPOINTMENT_CHANGE_NOTIFICATION_BODY` has been changed
    to to be used with a single `change` instead of `changes`.

## new features

-   It is now possible to delete a study domain and all related
    pseudonyms. Once a pseudonym is deleted, it is no longer possible to
    find the corresponding contact information. Note, however, that
    additional steps might be necessary for full anonymization of
    scientific data (e.g. image data).
-   It is now possible to assign conductors to individual appointments
    instead of participations. Email notifications are only sent to the
    assigned conductors.
-   Assignments are no longer cleared when the status of a study
    changes.
-   `CASTELLUM_CUSTOM_PRIVACY_LEVELS` can be used to distinguish
    different reasons for assigning a privacy level to a subject.
-   The execution list can now be sorted by tags and number of
    appointments
-   Execution tags are now included in calendar feeds
-   "Onetime invitations" have been renamed to "anonymous invitations".
    Participations in anonymous invitations are now treated as "awaiting
    response", so they are deleted automatically when a study ends.
-   Recruitment consent and blocked are no longer considered legal bases
    for deceased subjects
-   In recruitment cleanup, the "Unsuitable" option now also includes
    subjects who no longer have recruitment consent.
-   It is now possible to add multiple members to a study at the same
    time.
-   Subscribing to calendar feeds has been simplified by using
    webcal links which can be handled by calendar software directly.
-   The "add to study" feature now warns that it is mainly meant for
    migration purposes.


# 0.73.2 (2022-03-21)

-   Fixed link to participations in subject overview
-   Fixed crash when editing users via the admin UI


# 0.73.1 (2022-03-15)

-   Fixed missing translations


# 0.73.0 (2022-03-15)

## bug fixes

-   Fixed resetting user token in admin UI
-   Fixed future due date in data protection dashboard
-   Fixed getting pseudonyms in execution for finished studies

## new features

-   Added script `cleanup_underage_consents` to remove recruitment
    consents for underage subjects 2 years after they have come of age.
-   Help subject managers to clear residual recruitment data if there is
    no recruitment consent.


# 0.72.1 (2022-03-02)

## security

-   Accounts that were deactivated by removing the `is_active` flag were
    still able to access data using their token (either via the API or
    from calendar feeds). Note that expired accounts were still blocked.

## bug fixes

-   Fixed resetting user tokens in the admin UI.


# 0.72.0 (2022-02-22)

## bug fixes

-   Better handling of errors when the scheduler is not available.

## new features

-   Identicons are used to represent subjects throughout the
    application.
-   The UI for cleaning up the recruitment list has been revised. We
    also made some changes to how it works:
    -   Cleaning up subject that do not match the current filters will
        no longer exclude subjects with unknown attributes.
    -   Cleanup will no longer exclude subjects that have a follow-up
        scheduled.
-   The recruitment consent now also shows which version of the consent
    document was confirmed and on which date.
-   The maintenance dashboard contains additional relevant information
    for each subject.
-   Most badges gained a short explanation in a tooltip.
-   The accessibility was improved. Most importantly, there is now an
    invisible link at the beginning of the page to skip directly to the
    main content.


# 0.71.1 (2022-02-01)

-   Fix cases in which all subjects would be included in the subject
    protection dashboard.


# 0.71.0 (2022-02-01)

## breaking changes

-   It is no longer possible to create appointments for subjects
    who are not participating. If the status is changed from
    "participating" to anything else, existing appointments are deleted.
    This has less potential for confusion than keeping the appointments
    but ignoring them.
-   The docker image is now based on Alpine 3.14 which might cause
    issues if used with a docker version before 20.10.

## security

-   If available, django-axes is now also used to block brute-force
    attacks on API views. Previously it was only used on the login view.
    Django-axes is available by default in the official docker image.
-   In production setups, Django by default sends error reports to the
    email addresses defined in the `ADMINS` setting. These reports
    potentially contain sensitive data, e.g. session IDs. Starting with
    this version, Castellum cuts down the amount of information
    contained in these reports. You can restore the original behavior
    using the `DEFAULT_EXCEPTION_REPORTER` setting.

## bug fixes

-   Fixed a crash in the subjects pseudonyms view
-   Fixed cases in which subject creation requests were imported a
    second time after they had already been processed.
-   Fixed an indeterministic crash in the `create_demo_content` command.

## new features

-   It is now possible to add more than one resource to a session.
-   The users who are allowed to access a general domain are now defined
    in the admin UI for domains, not users.
-   Study tags are now displayed more prominently.
-   The "potential subjects" counts in study management now exclude
    subjects who are already participating or excluded.
-   JSON files in attribute export now use UTF-8 encoding instead of
    ASCII with escape codes.


# 0.70.2 (2022-01-12)

-   Enabled cache busting
-   Fixed width of alert in member management
-   Fixed error on invalid placeholders in resource URL
-   Fixed duplicate display of attribute options
-   Gracefully handle mail server errors in mail recruitment
-   Ignore `notify_to_be_deleted` for estranged subject maintenance view


# 0.70.1 (2022-01-11)

-   Fixed a broken migration


# 0.70.0 (2022-01-11)

## security

-   The calendars that are displayed in different parts of castellum
    constantly poll for new events. This was counted as user activity
    and therefore prevented the auto-logout mechanism to work correctly.
    With this release these requests are ignored when checking for user
    activity.

## breaking changes

-   `CASTELLUM_PSEUDONYMS_API_ENABLED` was renamed/extended to
    `CASTELLUM_API_ENABLED`
-   The execution API URLs changed (see docs/API.md for details)

## bug fixes

-   Fixed some missing fields in study duplication
-   Fixed various issues (including crashes) in the
    `fetch_scheduler_appointments` command
-   Fixed crash when trying to edit a guardian in recruitment/execution
-   Fixed missing translation fallback for attribute options
-   Fixed phone number in subject creation requests

## new features

-   This release contains many UI changes. Highlights:
    -   Styling was updated to bootstrap 5
    -   Changed the study list layout
    -   Changed study member management to display a single table
    -   Changed the data protection dashboard to display a single list
-   In recruitment, recently active (and therefore potentially
    responsive) subjects are highlighted with a badge and a new sort
    option. There is also a new button to only add recently active
    subjects.
-   A subject's privacy level is now prominently displayed in the UI,
    including recruitment and execution. A user's privacy level is
    correspondingly displayed in member management. This way it is
    easier to see whether your coworkers are allowed to access a
    specific subject.
-   There is a new subject maintenance view for subjects that have not
    been contacted in a long time.
-   The email address is now included in study export/import
-   The data protection dashboard now also displays meaningful
    information when the request is overdue.
-   Scheduler appointments are now synced automatically for the whole
    study when a relevant view is used. Previously, only the
    appointments for a single subject were synced when relevant views
    for that subject were used.
-   When setting a schedule ID, castellum now checks whether that
    schedule actually exists.
-   A schedule ID can no longer be changed once an appointment exists to
    avoid synchronisation issues between the scheduler and castellum.
-   Added two new API endpoints to list studies and get study metadata
    (see docs/API.md for details)
-   General domains can now have exportable attributes that are
    available via a new API endpoint


# 0.69.2 (2021-12-01)

-   Fixed displaying external event feeds


# 0.69.1 (2021-11-30)

-   Fixed pseudonym migration


# 0.69.0 (2021-11-30)

You need to update to at least 0.68.0 before updating to this version.

## breaking changes

-   The primary key for the Subject model was changed from `Subject.id`
    (integer) to `Subject.uuid` (UUID) to effectively make enumeration
    attacks impossible.
-   The `attribute_export` command now requires a subject UUID instead
    of an ID.
-   Castellum will no longer prevent users from creating overlapping
    appointments because this turned out to be too inflexible in
    practice. The corresponding error messages have been downgraded
    to warnings.
-   There is no longer a datepicker for browsers that do not natively
    support one. This mostly affects Safari prior to 14.1.
-   The legacy scheduler API (`SchedulerPingView`) has been removed.
    Instead you can now use the new `fetch_scheduler_appointments`
    command. Additionally, scheduler events will automatically be
    fetched when users access an appointment view.

## bug fixes

-   External calendar feeds defined via `Resource.url` now properly
    support recurring events.
-   Users are now warned on invalid subject search queries instead of
    just showing no results.
-   Fixed crash in legal representative update view.

## new features

-   Calendars with events in different colors now contain a legend.
-   `Resource.url` can now contain `{start}` and `{end}` placeholders.
-   The external calendar feed from `Resource.url` is now also displayed
    in the resource manager calendar.
-   The execution progress view now displays participating and dropped
    out subjects separately.
-   `ContactCreationRequest` gained a free text `message` field.


# 0.68.1 (2021-11-10)

-   Fixed events from `Resource.url` showing up multiple times.


# 0.68.0 (2021-11-09)

You need to update to at least 0.67.0 before updating to this version.

## breaking changes

-   The default value for `CASTELLUM_APPOINTMENT_REMINDER_PERIOD` was
    increased from 2 days to 3 days.
-   `StudyTypeEventFeed` was removed. For most use cases you can use
    `Resource.url` instead.
-   `User.logout_timeout` and `LOGOUT_TIMEOUT_DEFAULT` were replaced by
    `CASTELLUM_LOGOUT_TIMEOUT`.
-   `Sudy.data_sensitivity` was removed.
-   `Study.custom_filter` was removed. If you need a similar
    functionality it is recommended to create a bespoke attribute and
    fill it automatically from a python script.
-   When accepting or discarding a `SubjectCreationRequest`, it is no
    longer deleted but only marked as deleted. The associated contact
    information is still deleted. This way you can discerne whether an
    incoming request has already been handled or not.

## bug fixes

-   Calendars now use more space for events to avoid cropping. The text
    is also available as a tooltip.
-   For studies that are one time invitations, display the number of
    contacted subjects instead of invited subjects in the overview.

## new features

-   Users can now be added as managers for resources. In that case they
    gain access to a resource calendar.
-   Resources can now reference external event feeds. This event feed is
    included in the recruitment calendar for studies that use this
    resource.
-   The study calendar now includes the number of required subjects.
    This helps finding potential capacity peaks.
-   `ContactCreationRequest` gained a `phone_number` field.


# 0.67.2 (2021-10-26)

-   Fixed adding newly created legal representatives (regression from
    0.67.0)


# 0.67.1 (2021-10-19)

-   Fixed a faulty migration.


# 0.67.0 (2021-10-19)

## security

-   Added a missing privacy level check in appointment feeds
-   Fixed a possible subject enumeration in the legal guardian form

## bug fixes

-   Fixed sending appointment reminders only once (regression from
    0.66.0)
-   In date inputs, limit the number of digits for the year to 4 (not
    supported in all browsers)

## new features

-   A common requirement we hear is that potential subjects should be
    able to register themselves to castellum by using a web form.
    Castellum is usually not reachable from the internet for security
    reasons. The solution is to have a separate form and create a cron
    job that automatically fetches new subjects from that form and adds
    them to castellum.

    However, that process would bypass the manual checks for duplicates
    and validity. For that reason we added a system to create "subject
    creation requests" that serve as an intermediate step. The cron job
    can create those requests. A human can then review and either accept
    or discard them.

    An example script for the cron job is available in
    `docs/scripts/fetch_from_self_registration.py`. The relevant UI can
    be enabled with the `CASTELLUM_SUBJECT_CREATION_REQUESTS_ENABLED`
    setting.
-   The castellum version number and release date are now displayed on
    the front page.
-   The subject search UI now automatically switches to the create tab
    if there are no matches.


# 0.66.0 (2021-09-28)

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
