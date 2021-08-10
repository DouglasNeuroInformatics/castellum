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

Monitoring
----------

In order to allow analysing suspicious behavior, critical actions such as
search, deletion, or login attempts are logged to a separate log file.
