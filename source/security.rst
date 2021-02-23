Security
========

The main purpose of castellum is to handle data of test subjects. It is
important to be able to read and write this data in various ways. We are
also legally required to provide some specific forms of access, e.g.
exporting or deleting all data on a single subject.

On the other hand, we are also required to handle this data very
carefully. Among other things, we are required to split the data so that
users can only ever access the parts of the data they really need.

The security measures outlined in this section are meant to only allow access
where allowed and required.

Account restrictions
--------------------

-  Users are automatically logged out on inactivity
-  User accounts expire on a set date

.. _permissions:

Permissions
-----------

Most actions in castellum are protected by one or more permission. For
easier handling, permissions are usually not assigned directly. Instead,
they are collected into meaningful groups (aka :ref:`roles`). Castellum comes
with some pre-defined sample groups, but you can adapt them to your needs.

Note that the django framework automatically generates a lot of
permissions. Only a few of them are actually used. The full list is:

-  ``studies.approve_study``
-  ``studies.view_study``
-  ``studies.change_study``
-  ``studies.delete_study``
-  ``studies.access_study``
-  ``subjects.view_subject``
-  ``subjects.change_subject``
-  ``subjects.delete_subject``
-  ``subjects.export_subject``
-  ``recruitment.recruit``
-  ``recruitment.conduct_study``
-  ``recruitment.search_participations``
-  ``recruitment.view_current_appointments``
-  ``recruitment.change_appointments``
-  ``castellum_auth.privacy_level_1``
-  ``castellum_auth.privacy_level_2``

Study membership
~~~~~~~~~~~~~~~~

If a user is a member of a study, they automatically gain the special
``access_study`` permission in the context of that study. You can also
assign additional groups to study members that only apply in the context
of the study.

.. _privacy-level:

Privacy levels
~~~~~~~~~~~~~~

Every subject has a privacy level. A user is only allowed to access that
subject if they have a sufficient privacy level themselves. For recruitment
attributes, you can define separate privacy levels for read and write access. A
user's privacy level is controlled via the special permissions
``privacy_level_1`` and ``privacy_level_2``. The three levels (0-2) accord to
the data security levels of the Max Planck Society.

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

Data separation
---------------

Implementation
~~~~~~~~~~~~~~

We chose to split the data into three different categories:

-  Scientific data is handled outside of castellum. Castellum only
   provides the pseudonyms that are used to map this data to subjects.
-  Data relevant for recruitment is handled in castellum.
-  Contact data is also handled in castellum, but in a separate database
   to provide an additional barrier.

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

The described architecture provides a clear structure for developers
that should help avoiding critical data leaks. Even if an attacker is
able to dump a whole table or even a whole database, this structure
still limits the impact.

However, it is important to understand that the barrier between
recruitment and contact data is not that high. Since castellum has full
access to both, an attacker can also gain full access. Spreading the
system across several databases on different servers or even in
different organizations does not help much if there is still a single
point of entry.

Monitoring
----------

In order to allow analysing suspicious behavior, critical actions such as
search, deletion, or login attempts are logged to a separate log file.
