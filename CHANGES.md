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
