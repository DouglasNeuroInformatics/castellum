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
