# Pseudonyms

Castellum allows you to keep the subject's contact information in a
central place and use pseudonyms everywhere else.

Subjects can have multiple pseudonyms. To know which is which, each
pseudonym is tied to a *coding list*. There can be only one
pseudonym for a subject in each coding list.

## General coding lists

Most coding lists are linked to an object in Castellum, usually a study. But
there can also be so called *general coding lists* which are not linked to
anything in Castellum. These can be useful to provide pseudonyms for
external databases that are used accross studies, e.g. for blood samples
or IQ scores.

In order to use a general coding list you need to perform these steps:

-   In the admin UI, create a coding list that has a blank `content_type`
    and `object_id`.
-   In the same UI, select which users need to be able to access this
    general coding list.
-   Also in the same UI, select which attributes need to be accessible
    for this coding list via the API.
-   Study coordinators can then select which general coding list they need to
    access in their study.

## Legacy pseudonyms

Castellum will automatically generate pseudonyms for subjects. However,
when importing subjects from a different system, there may already be
existing pseudonyms that should not be lost. This section will describe
how those legacy pseudonyms can be imported into Castellum.

### Import data

To import legacy pseudonyms you first need to create such a coding list.
After that you can create the pseudonyms themselves:

    from castellum.pseudonyms.models import CodingList
    from castellum.pseudonyms.models import Pseudonym

    mydata = […]

    my_coding_list = CodingList.objects.create()
    print(my_coding_list.key)

    for subject, legacy_pseudonym in mydata:
        Pseudonym.objects.create(
            subject=subject,
            coding_list=my_coding_list
            pseudonym=legacy_pseudonym,
        )

### Adapt validation

Pseudonyms entered by users are validated. Since legacy pseudonyms will
usually have a different format, you need to globally disable that
validation in the settings:

    CASTELLUM_PSEUDONYM_CLEAN = lambda x: x

Of course you can also write a custom validation that can handle the
legacy pseudonyms.
