# Pseudonyms

Castellum allows you to keep the subject's contact information in a
central place and use pseudonyms everywhere else.

Subjects can have multiple pseudonyms. To know which is which, each
pseudonym is tied to a *pseudonym domain*. There can be only one
pseudonym for a subject in each domain.

## General domains

Most domains are linked to an object in Castellum, usually a study. But
there can also be so called *general domains* which are not linked to
anything in Castellum. These can be useful to provide pseudonyms for
external databases that are used accross studies, e.g. for blood samples
or IQ scores.

In order to use a general domain you need to perform these steps:

-   In the admin UI, create a domain that has a blank `content_type`
    and `object_id`. There you can also select which attributes need to
    be accessible for this domain via the API.
-   Also in the admin UI, add the domain to the "available general
    domains" for relevant users.
-   Study coordinators can then select which general domain they need to
    access in their study.

## Legacy pseudonyms

Castellum will automatically generate pseudonyms for subjects. However,
when importing subjects from a different system, there may already be
existing pseudonyms that should not be lost. This section will describe
how those legacy pseudonyms can be imported into Castellum.

### Import data

To import legacy pseudonyms you first need to create such a domain.
After that you can create the pseudonyms themselves:

    from castellum.pseudonyms.models import Domain
    from castellum.pseudonyms.models import Pseudonym

    mydata = […]

    mydomain = Domain.objects.create()
    print(mydomain.key)

    for subject, legacy_pseudonym in mydata:
        Pseudonym.objects.create(
            subject=subject,
            domain=mydomain
            pseudonym=legacy_pseudonym,
        )

### Adapt validation

Pseudonyms entered by users are validated. Since legacy pseudonyms will
usually have a different format, you need to globally disable that
validation in the settings:

    CASTELLUM_PSEUDONYM_CLEAN = lambda x: x

Of course you can also write a custom validation that can handle the
legacy pseudonyms.
