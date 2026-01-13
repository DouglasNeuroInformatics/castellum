Pseudonyms
==========

Scientific data should never be stored with a subject's name. Instead,
Castellum provides pseudonyms that can be used to link the data back to the
subject. Anyone who wants to get in contact with a subject should have to go
through castellum.

.. warning::
    Traces of contact data can also exist in the systems that are used for
    communication, e.g. email servers or payment providers.

A subject can have many different pseudonyms in different pseudonym lists.
Castellum automatically creates a new pseudonym list for each study. There can
be more than one pseudonym list per study as well as *general pseudonym lists*
that are not connected to studies at all. You can think of these pseudonym
lists just as paper lists with names and pseudonyms, except that these lists
are handled by Castellum in the background and you never get to see the
complete list.

Pseudonyms are only unique (and therefore useful) in the context of a pseudonym
list. Whenever you use a pseudonym, make sure that it is clear which pseudonym
list it belongs to. If in doubt, store the identifier of the pseudonym list
along with the pseudonym.

It is up to you to decide on a granularity of pseudonym lists. For example you
could use a single pseudonym list for all bio samples. Or you could use
separate pseudonym lists for blood, saliva, stool, ….

Using study pseudonyms
----------------------

Whenever you collect data in the context of a study, it should be stored with a
study pseudonym. Pseudonyms can also be printed on questionnaires or passed to
external survey services.

Relevant guides:

-   :ref:`study-pseudonym-lists`
-   :ref:`subject-by-pseudonym`
-   :ref:`subject-by-general-pseudonym`
-   :ref:`subject-get-pseudonym`
-   :ref:`execution-attribute-export`

.. _general-pseudonym-lists:

Using pseudonyms from general pseudonym lists
---------------------------------------------

Central repositories (e.g. for bio samples or IQ scores) often store data that
is not related to a specific study. In these cases, you can use a *general
pseudonym list*.

Because these pseudonyms are the same across all studies, access to them is
highly restricted. Both the user and the study need to be authorized before it
shows up in list of pseudonyms.

Relevant guides:

-   :ref:`admin-general-pseudonym-lists`
-   :ref:`admin-users`
-   :ref:`study-pseudonym-lists`
-   :ref:`subject-get-pseudonym`
-   :ref:`subject-delete`

Deleting pseudonym lists
------------------------

It is possible to delete a pseudonym list and all related pseudonyms. Once a
pseudonym is deleted, it is no longer possible to find the corresponding
contact information. Note, however, that additional steps might be necessary
for full anonymization of scientific data (e.g. image data).

The date when a study pseudonym list should be deleted is usually defined in
the ethics application and the study consent form.

How pseudonyms are generated
----------------------------

Castellum generates random pseudonyms and stores them in a database.

An alternative approach for generating pseudonyms would be to calculate an
encrypted hash over immutable, subject-related information (e.g. name, date of
birth). That approach would have the benefit of not relying on a central
infrastructure to store the pseudonyms. However, in cases where such a central
infrastructure with strict access control is feasible, Castellum's approach is
much simpler. For more information on these two approaches, see `Anforderungen
an den datenschutzkonformen Einsatz von Pseudonymisierungslösungen (german)
<https://www.de.digital/DIGITAL/Redaktion/DE/Digital-Gipfel/Download/2018/p9-datenschutzkonformer-einsatz-von-pseudonymisierungsloesungen.pdf>`_.

The algorithm that is used to generate pseudonyms can be configured. The
default algorithm uses digits and uppercase letters. In order to avoid mixups,
the letters "O", "I", "S", and "B" never appear in a pseudonym. When a user
enters those letters, they are automatically replaced by "0", "1", "5", or "8"
respectively. Single typos are guaranteed to be detected. This algorithm is
also available as a `standalone python package
<https://pypi.org/project/castellum-pseudonyms/>`_ so you can validate
pseudonyms in your scripts and pipelines.
