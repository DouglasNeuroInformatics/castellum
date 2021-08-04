Data separation
===============

At its core, Castellum is about splitting a subject's data into little pieces.
On the one hand this means that users can only access the pieces that are
necessary for them. On the other hand this means that castellum contains the
necessary information to but all the pieces back together, e.g. so it can be
deleted on request

Pseudonyms
----------

There are generally two approaches to generate pseudonyms:

-   Calculate an encrypted hash over immutable, subject-related information
    (e.g. name, date of birth)
-   Generate a random pseudonym and store it in a mapping table

The former approach has the benefit of not relying on a central infrastructure.
However, in cases where such a central infrastructure with strict access
control is feasible, the latter approach is much simpler.

Castellum implements the latter approach.

For more information on these two approaches, see `Anforderungen an den
datenschutzkonformen Einsatz von Pseudonymisierungslösungen (german)
<https://www.de.digital/DIGITAL/Redaktion/DE/Digital-Gipfel/Download/2018/p9-datenschutzkonformer-einsatz-von-pseudonymisierungsloesungen.pdf>`_.

The algorithm that is used to generate pseudonyms can be configured. The
algorithm that is used by default produces alphanumeric strings with 20 bits of
entropy and two checkdigits that are guaranteed to detect single errors. It is
also available as a `standalone package
<https://pypi.org/project/castellum-pseudonyms/>`_.

Database split
--------------

In Castellum, contact data is handled in a separate database server from
everything else to provide an additional barrier.

This provides a clear structure for developers that should help avoiding
critical data leaks. Even if an attacker is able to dump a whole table or even
a whole database, this structure still limits the impact.

However, it is important to understand that the barrier between recruitment and
contact data is not that high. Since castellum has full access to both, an
attacker can also gain full access. Spreading the system across several
databases on different servers or even in different organizations does not help
much if there is still a single point of entry.
