Security Considerations
=======================

Castellum does not store sensitive research data by itself. However, it
stores the names and contact details of participants, as well as the
pseudonyms that link them to research data. This makes Castellum a
security critical part of your infrastructure.

This document provides an overview of common attacks and the
corresponding mitigations in Castellum, as well as additional steps that
are needed beyond that.

General Threats
---------------

Castellum incorporates several features to address common security
threats:

-   **Protection Against Common Attacks**: Castellum is built on top of
    the Django framework, which already comes with solid safeguards
    against cross-site request forgery (CSRF) and SQL injection attacks.
    For more details, refer to the `Django Security
    Documentation <https://docs.djangoproject.com/en/5.2/topics/security/>`__.
-   **Content Security Policy (CSP)**: A robust Content Security Policy
    is implemented to mitigate a wide range of cross-site scripting (XSS)
    attacks.
-   **Two-Factor Authentication (2FA)**: To reduce the risks associated
    with weak passwords, Castellum supports two-factor authentication.
    While this feature is optional, it can be enforced using
    ``MFAEnforceMiddleware``. Additionally, consider enforcing FIDO2
    keys, which have several benefits (e.g. phishing resistance) compared
    to TOTP keys. See `django-mfa3 <https://github.com/xi/django-mfa3>`__
    for details.

However, it is crucial to ensure that the underlying infrastructure is
also secure. Key recommendations include:

-   **Unauthorized Access**: Make sure to check the security of
    databases, HTTP servers, SSH daemons, and account management.
-   **Backups**: Make sure to have working backups to prevent data loss.
-   **Training**: Regularly train users to prevent phishing attacks,
    social engineering, or leaving unlocked laptops.
-   **Admins**: Be aware that system administrators can see and edit any
    information in the database.

Threats From Participants
-------------------------

-   **Proximity**: When using Castellum during a lab session, make sure
    that participants can never see data of other subjects, and never
    leave participants alone with an unlocked device. Castellum will
    automatically log out users after some time of inactivity
    (``CASTELLUM_LOGOUT_TIMEOUT``), but you should not rely on that.
-   **Impersonation**: There is a risk that attackers may attempt to
    impersonate participants to extract sensitive information. Always
    verify the identity of individuals requesting information or changes
    to their data.
-   **Incorrect information**: When making critical decisions, you should
    not solely rely on the information stored in Castellum. For example,
    before conducting procedures such as an MRI, always verify that
    participants do not have contraindications, such as a pacemaker.
-   **Reliability**: Participants may make multiple appointments and fail
    to show up, wasting valuable resources. Castellum includes a feature
    to :ref:`track participant reliability <execution-annotations>`,
    allowing staff to identify and exclude individuals who frequently miss
    appointments.
-   **Threat to Staff**: Participants may be aggressive or even violent
    towards staff members. Castellum provides functionality to :ref:`block
    participants <subject-block>` in such cases, even against their will,
    based on legitimate interests.

Threats From Users
------------------

.. _privacy-level:

Background: Access Restrictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Castellum uses three orthogonal mechanisms to limit which data users
have access to:

-   **Permissions**: Most actions in Castellum are protected by one or
    more permission. For easier handling, permissions are usually not
    assigned directly. Instead, they are collected into meaningful groups
    (aka :ref:`roles`). Castellum comes with some pre-defined sample
    groups, but you can adapt them to your needs.
-   **Study memberships**: Study coordinator can also assign additional
    groups to study members that only apply in the context of the study.
    For example, a student aid may be a recruiter in one study, but have
    no permissions beyond that.
-   **Privacy levels**: Every subject has a privacy level (regular,
    increased, or high). A user is only allowed to access that subject if
    they have a sufficient privacy level themselves. A user's privacy
    level is controlled via the special permissions ``privacy_level_1``
    and ``privacy_level_2``.

Breaking Out of Studies
~~~~~~~~~~~~~~~~~~~~~~~

Restricting users to specific studies is one of Castellum's fundamental
security features. However, there are several scenarios where this
restriction cannot be enforced effectively:

-   **Recruiters** are granted access to a random sample of potential
    participants for their studies. They can in theory gain access to
    arbitrary subjects by increasing the size of that sample:

    -   For manual recruitment, the number of subjects in "not contacted"
        status is limited. Recruiters can still add more by changing the
        participation status of existing entries.
    -   For mail recruitment, there is no limit, but subjects would
        receive an email, which makes it harder to abuse this feature
        undetected.
    -   By default, recruiters can only see the information necessary to
        contact potential participants. In practice however it is often
        necessary to also allow them to see and update recruitment
        attributes and consents.

-   **Study coordinators** can create a study and give themselves
    additional permissions within that context.

    -   The set of :ref:`study-roles` controls which additional
        permissions a study coordinator may acquire. By default, only a
        minimal set of roles is available. If you want to add additional
        roles, you should carefully consider the risks and benefits.
    -   All studies need to be approved before they can start recruitment.
        The approver should check for suspicious settings before approving
        the study. However, for practical reasons all study settings
        (including memberships) can still be changed after the approval.
        Some organizations will even choose to allow study coordinators to
        approve their own studies.

-   **Targeted filters**: Even if a study has not been approved, study
    coordinators may be able to exploit attribute filters to extract
    information about individual subjects. Filters provide a preview of
    the number of matches. So if the study coordinator manages to design
    a filter that only matches a single subject, they can deduce the
    values for all other attributes.

    To mitigate this risk, the preview has limited granularity (e.g.
    "<10"). Also, age filters cannot be restricted to a single date of
    birth.

-   **Adding new subjects**: When adding new subjects to the database,
    users must first check whether the subjects already exist. As a
    consequence, these users need access to all subjects in the database,
    not just in their study. It is strongly recommended to delegate this
    task to few trusted staff members rather than granting global access
    to all users.

-   **Managing legal representatives**: While users who can access a
    subject can also edit the subject's legal representatives, they are
    not allowed to add new legal representatives. That combination would
    allow them to add an arbitrary subject as a legal representative and
    access their data. Again, this task should be reserved for few select
    users with global access.

All of these scenarios represent legitimate use cases that nonetheless
carry the potential for abuse. Often, such abuse stems from legitimate
needs. It is essential for organizations to find a balance between
implementing necessary restrictions and allowing users to perform their
jobs effectively.

This can include clear guidelines on who gets which permissions, how
users with less permissions can get support from users with more
permissions, as well as robust processes to monitor, detect, and prevent
any misuse of the system.

Spam
~~~~

While contacting potential participants is a fundamental aspect of
recruitment, excessive contact attempts can lead to the participant
disengagement, which ultimately harms all studies.

To mitigate this issue, Castellum limits studies to a single reminder
for recruitment mails. Additionally, subjects will not be proposed for
new studies if they have recently been contacted, as configured via
``CASTELLUM_PERIOD_BETWEEN_CONTACT_ATTEMPTS``.

Competition Among Studies
~~~~~~~~~~~~~~~~~~~~~~~~~

Aggressive recruitment efforts by one study can deplete the available
participant pool for others. To address this, study approvers should
monitor recruitment activity and stop studies that exceed reasonable
limits.

The settings ``CASTELLUM_RECRUITMENT_HARD_LIMIT_FACTOR`` and
``CASTELLUM_RECRUITMENT_MAIL_WEEKLY_LIMIT`` can also help in limiting
recruitment activity by individual studies.

Bypassing Castellum
~~~~~~~~~~~~~~~~~~~

Castellum can only provide support if it is being used in the first
place. Failure to do so will result in unmanaged personal data, which
can lead to incomplete responses to GDPR export, rectification, or
deletion requests.

-   **Incomplete participant list**: Researchers may neglect to enter all
    study participants into Castellum.
-   **Not using Pseudonyms**: Researchers might keep a redundant list of
    contact data instead of using the pseudonyms provided by Castellum.
-   **Inadequate Deletion**: Data protection coordinators may neglect to
    delete data that no longer have a legal basis.

Database Separation
-------------------

Contact data is stored in a separate database from everything else. Even
if an attacker is able to dump a whole database, this structure still
limits the impact. However, since Castellum has full access to both
databases, an attacker who takes over the server can also gain full
access. Spreading the system across several databases does not help much
if there is still a single point of entry.

.. _audit-trail:

Audit Trail
-----------

In order to allow detecting suspicious behavior, critical actions such
as search, deletion, or login attempts can be recorded. This feature is
disabled by default, but can be enabled using the
``CASTELLUM_AUDIT_TRAIL_ENABLED`` setting.

Users can have limited access to the audit trail if they have either the
``subjects.view_audit_trail`` or the ``studies.view_audit_trail``
permission.

Additionally, the setting ``CASTELLUM_MONITORING_INCLUDE_SEARCH`` can be
used to control whether the audit trail records subject searches. This
allows to detect users who abuse this feature. On the other hand, the
search text usually contains personal information such as names and
email addresses. It depends on the specific threat model whether it
should be enabled or not.

.. _permissions:

Annex: Full List of Permissions
-------------------------------

While Castellum comes with a set of default groups, it is likely that
organizations will have to fine-tune them to their specific needs. In
that case, it is important to understand the underlying permissions.

Most permissions have descriptive names. However, the Django framework
automatically generates a lot of permissions that are not used. It can
be hard to find the relevant permissions among that noise.

These are the permissions that are actively used:

-   ``studies.approve_study``
-   ``studies.view_study``
-   ``studies.change_study``
-   ``studies.delete_study``
-   ``studies.access_study``
-   ``studies.view_audit_trail``
-   ``subjects.view_subject``
-   ``subjects.change_subject``
-   ``subjects.delete_subject``
-   ``subjects.add_to_study``
-   ``subjects.list_participations``
-   ``subjects.export_subject``
-   ``subjects.view_audit_trail``
-   ``subjects.view_report``
-   ``contacts.view_blockhash``
-   ``recruitment.recruit``
-   ``recruitment.conduct_study``
-   ``recruitment.change_appointments``
-   ``appointments.view_current_appointments``
-   ``castellum_auth.privacy_level_1``
-   ``castellum_auth.privacy_level_2``
