Security
========

Account restrictions
--------------------

-  Users are automatically logged out on inactivity
-  User accounts expire on a set date
-  (Mandatory) :ref:`2fa`

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
``access_study`` permission in the context of that study. Study managers can
also assign additional groups to study members that only apply in the context
of the study.

.. warning::
    By managing study memberships, study managers can escalate their own
    priviliges inside their studies. For example, they can allow themselves to
    see recruitment attributes of participants.

    All studies need to be approved before they can start recruitment. The
    approver should check for suspicious settings before approving the study.
    However, for practical reasons all study settings (including memberships)
    can still be changed after the approval. Some organizations will even
    choose to allow study managers to approve their own studies.

.. _privacy-level:

Privacy levels
~~~~~~~~~~~~~~

Every subject has a privacy level. A user is only allowed to access that
subject if they have a sufficient privacy level themselves. For recruitment
attributes, you can define separate privacy levels for read and write access. A
user's privacy level is controlled via the special permissions
``privacy_level_1`` and ``privacy_level_2``. The three levels (0-2) accord to
the data security levels of the Max Planck Society.

Access to resources and general domains
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to how a study membership allows a user to access a specific study,
users need to be authorized to access specific resources and :ref:`general
domains <general-domains>`. This can only be done by administrators.

Database separation
-------------------

We chose to split the data into three different categories:

-  Scientific data is handled outside of castellum. Castellum only
   provides the pseudonyms that are used to map this data to subjects.
-  Data relevant for recruitment is handled in castellum.
-  Contact data is also handled in castellum, but in a separate database
   to provide an additional barrier.

Storing contact data in a separate database provides a clear structure for
developers that should help avoiding critical data leaks. Even if an attacker
is able to dump a whole table or even a whole database, this structure still
limits the impact.

However, it is important to understand that the barrier between recruitment and
contact data is not that high. Since castellum has full access to both, an
attacker can also gain full access. Spreading the system across several
databases on different servers or even in different organizations does not help
much if there is still a single point of entry.

Monitoring
----------

In order to allow analysing suspicious behavior, critical actions such as
search, deletion, or login attempts are logged to a separate log file.
