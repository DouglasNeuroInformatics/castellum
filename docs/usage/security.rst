Security Measures
=================

Account restrictions
--------------------

-  Users are automatically logged out on inactivity
-  User accounts expire on a set date
-  :ref:`2fa` (can be made mandatory)

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
-  ``studies.view_audit_trail``
-  ``subjects.view_subject``
-  ``subjects.change_subject``
-  ``subjects.delete_subject``
-  ``subjects.export_subject``
-  ``subjects.view_audit_trail``
-  ``subjects.view_report``
-  ``recruitment.recruit``
-  ``recruitment.conduct_study``
-  ``recruitment.change_appointments``
-  ``appointments.view_current_appointments``
-  ``castellum_auth.privacy_level_1``
-  ``castellum_auth.privacy_level_2``

Study membership
~~~~~~~~~~~~~~~~

If a user is a member of a study, they automatically gain the special
``access_study`` permission in the context of that study. Study coordinator can
also assign additional groups to study members that only apply in the context
of the study.

.. warning::
    By managing study memberships, study coordinator can **escalate their own
    priviliges** inside their studies. For example, they can allow themselves to
    access information about the participants. Still, there are mechanisms that
    limit the impact of this privilige escalation:

    -   The set of :ref:`study-roles` controls which additional permissions a
        study coordinator may gain. By default, only a minimal set of roles is
        available. If you want to add additional roles, you should carefully
        consider the risks and benefits.
    -   All studies need to be approved before they can start recruitment. The
        approver should check for suspicious settings before approving the
        study. However, for practical reasons all study settings (including
        memberships) can still be changed after the approval. Some
        organizations will even choose to allow study coordinator to approve
        their own studies.
    -   Changes to study memberships are :ref:`monitored <audit-trail>` so that
        abuse can be detected.

.. _privacy-level:

Privacy levels
~~~~~~~~~~~~~~

Every subject has a privacy level. A user is only allowed to access that
subject if they have a sufficient privacy level themselves. A
user's privacy level is controlled via the special permissions
``privacy_level_1`` and ``privacy_level_2``. The three levels (0-2) accord to
the data security levels of the Max Planck Society.

Access to resources and general pseudonym lists
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to how a study membership allows a user to access a specific study,
users need to be authorized to access specific resources and :ref:`general
pseudonym lists <general-pseudonym-lists>`. This can only be done by
administrators.

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
limits the impact. An attacker without access to castellum would need physical
access to both databases in order to get the same level of access as with
castellum.

However, it is important to understand that the barrier between recruitment and
contact data is not that high. Since castellum has full access to both, an
attacker can also gain full access. Spreading the system across several
databases on different servers or even in different organizations does not help
much if there is still a single point of entry.

.. _audit-trail:

Audit Trail
-----------

In order to allow analysing suspicious behavior, critical actions such as
search, deletion, or login attempts can be recorded by enabling the
``CASTELLUM_AUDIT_TRAIL_ENABLED`` setting.

Users can have limited access to the audit
trail if they have either the ``subjects.view_audit_trail`` or the
``studies.view_audit_trail`` permission.

Additionally, the setting ``CASTELLUM_MONITORING_INCLUDE_SEARCH`` can be
used to control whether the audit trail records subject searches. This allows
to detect users who abuse this feature. On the other hand, the search text
usually contains personal information such as names and email addresses. It
depends on the specific threat model whether it should be enabled or not.
