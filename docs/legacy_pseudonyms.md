# Legacy Pseudonyms

Castellum will automatically generate pseudonyms for subjects. However,
when importing subjects from a different system, there may already be
existing pseudonyms that should not be lost. This document will describe
how those legacy pseudonyms can be imported into Castellum.

# Import data

In Castellum, a subject can have multiple pseudonyms. To know which is
which, each pseudonym is tied to a *pseudonym domain*. There can be only
one pseudonym for a subject in each domain.

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

# Adapt validation

Pseudonyms entered by users are validated. Since legacy pseudonyms will
usually have a different format, you need to globally disable that
validation in the settings:

    CASTELLUM_PSEUDONYM_CLEAN = lambda x: x

Of course you can also write a custom validation that can handle the
legacy pseudonyms.
