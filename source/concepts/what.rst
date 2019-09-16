What is this?
=============

Castellum is a subject database system developed at the Max Planck Society.

Goals
-----

-   GDPR compliant data protection and security
-   Flexibility so it can be used in different institutes

Classification
--------------

You can think of many kinds of scientific databases that handle personal
information:

study database
    contains all data that is collected during a study

    only the researchers that are involved with the study have access to
    the data

study archive
    contains data from past studies that is relevant for scientific
    reasons, e.g. reproducibility

research archive
    contains data that has been collected during one study, but may be
    reused in another one

    reusing data saves time for both the researcher and the test subject

    examples include image archives and biobanks

recruting database
    contains some data about (potential) test subjects that allows you can
    find out which ones you should contact for your next study

contact database
    a central list of contact information shared by all other databases

    by having this in a central place, contact information can be updated
    for all studies at the same time.

    by having this in a central place, the other databases can work with
    pseudonyms instead.

pseudonym service
    used to store relations between the different datasets

Of these, castellum implements a recruting database, a contact database, and a
pseudonym service. All data that is actually related to studies must be
stored separately.
