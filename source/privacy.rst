Privacy
=======

At its core, Castellum is about splitting a subject's data into little pieces.
On the one hand this means that users can only access the pieces that are
necessary for them. On the other hand this means that castellum contains the
necessary information to put all the pieces back together, e.g. so it can be
deleted on request.


Contact data
------------

Contact details are stored in Castellum itself. This means that anyone who
wants to get in contact with a subject needs to go through castellum.

.. warning::
    Traces of contact data can also exist in the systems that are used for
    communication, e.g. email servers or payment providers.


Pseudonyms
----------

Scientific data should never be stored with a subject's name. Instead,
Castellum automatically generates and stores random pseudonyms that can be used
to link the data back to the subject.

.. note::
    An alternative approach for generating pseudonyms would be to calculate an
    encrypted hash over immutable, subject-related information (e.g. name, date
    of birth)

    That approach would have the benefit of not relying on a central
    infrastructure to store the pseudonyms. However, in cases where such a
    central infrastructure with strict access control is feasible, Castellum's
    approach is much simpler.

    For more information on these two approaches, see `Anforderungen an den
    datenschutzkonformen Einsatz von Pseudonymisierungslösungen (german)
    <https://www.de.digital/DIGITAL/Redaktion/DE/Digital-Gipfel/Download/2018/p9-datenschutzkonformer-einsatz-von-pseudonymisierungsloesungen.pdf>`_.

.. note::
    The algorithm that is used to generate pseudonyms can be configured. The
    algorithm that is used by default produces alphanumeric strings with 20
    bits of entropy and two checkdigits that are guaranteed to detect single
    errors. It is also available as a `standalone package
    <https://pypi.org/project/castellum-pseudonyms/>`_.

A subject can have many different pseudonyms in different domains. Castellum
automatically creates a new domain for each study. There can be more than one
domain per study as well as *general domains* that are not connected to studies
at all.

.. warning::
    Pseudonyms are only unique (and therefore useful) within their domain.
    Whenever you use a pseudonym, make sure that it is clear which domain it
    belongs to. If in doubt, store the domain along with the pseudonym.

It is up to you to decide on a granularity of domains. For example you could
use a single domain for all bio samples. Or you could use separate domains for
blood, saliva, stool, ….

Using study pseudonyms
~~~~~~~~~~~~~~~~~~~~~~

Whenever you collect data in the context of a study, it should be stored with a
study pseudonym. Pseudonyms can also be printed on questionnaires or passed to
external survey services.

Relevant guides:

-   :ref:`study-domains`
-   :ref:`subject-by-pseudonym`
-   :ref:`subject-get-pseudonym`

.. todo::
    -   attribute export

Using pseudonyms from general domains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Central repositories (e.g. for bio samples or IQ scores) often store data that
is not related to a specific study. In these cases, you can use pseudonyms from
a *general domain*.

Because these pseudonyms are the same across all studies, access to them is
highly restricted. Both the user and the study need to be authorized before it
shows up in list of pseudonyms. This also means that, even though general
domains exist independently of studies, they can only be accessed through
studies.

Relevant guides:

-   :ref:`admin-general-domains`
-   :ref:`admin-users`
-   :ref:`study-domains`
-   :ref:`subject-get-pseudonym`
-   :ref:`subject-delete`


Database split
--------------

In Castellum, contact data is handled in a database server which is separated
from everything else to provide an additional barrier.

This provides a clear structure for developers that should help avoiding
critical data leaks. Even if an attacker is able to dump a whole table or even
a whole database, this structure still limits the impact.

However, it is important to understand that the barrier between recruitment and
contact data is not that high. Since castellum has full access to both, an
attacker can also gain full access. Spreading the system across several
databases on different servers or even in different organizations does not help
much if there is still a single point of entry.
