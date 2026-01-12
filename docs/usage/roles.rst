.. _roles:

Roles
=====

.. note::

    This section lists the roles that castellum ships by default. Administrators
    can customize these roles for their organization.

Study specific roles, in contrast to global ones, only take effect in the
context of a study. They can be assigned in **Member Management** by the
**Study Coordinator**.

.. _global-roles:

Global roles
------------

Subject Manager
~~~~~~~~~~~~~~~

The **Subject Manager** enters data records of subjects in Castellum
and makes changes to existing ones.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`subject-create`
-   :ref:`subject-edit`
-   :ref:`subject-to-be-deleted`
-   :ref:`subject-report`
-   :ref:`subject-consent`
-   :ref:`subject-add-to-study`

Study Coordinator
~~~~~~~~~~~~~~~~~

The study coordination is embodied by the **Study Coordinator**. This person
inserts studies into the database and defines the settings for them.

Relevant guides:

-   :ref:`study-create`
-   :ref:`study-members`
-   :ref:`study-sessions`
-   :ref:`study-recruitment-settings`
-   :ref:`study-pseudonym-lists`
-   :ref:`study-finish`
-   :ref:`study-delete-pseudonym-lists`
-   :ref:`study-delete`
-   :ref:`scheduler-setup`

Study Approver
~~~~~~~~~~~~~~

Study Coordinators by default cannot start their own studies. Instead, they
have to ask a **Study Approver** to review and start the study.

If you want to be less strict about this, you can either modify the Study
Coordinator role or make all Study Coordinators also Study Approvers.

Relevant guides:

-   :ref:`study-start`

Receptionist
~~~~~~~~~~~~

Receptionists can access the list of today's appointments. That way they can
help subjects who come to the institute without needing information from each
study individually.

Relevant guides:

-   :ref:`reception`

Data Protection Officer
~~~~~~~~~~~~~~~~~~~~~~~

The group of people responsible for data protection should take on the role of
**Data Protection Officer**. Castellum supports these users by providing a
**data protection dashboard** that collects all relevant information in a
single place.

Relevant guides:

-   :ref:`data-protection-dashboard`
-   :ref:`subject-export`
-   :ref:`subject-delete`
-   :ref:`subject-block`
-   :ref:`study-delete`

Administrator
~~~~~~~~~~~~~

**Administrators** are in charge of defining basic structures and performing
privileged actions.

Relevant guides:

-   :ref:`admin-users`
-   :ref:`admin-unlock`
-   :ref:`admin-compromised`
-   :ref:`admin-roles`
-   :ref:`admin-attributes`
-   :ref:`admin-consent-document`

.. TODO::

    -   manage resources


.. _study-roles:

Study specific roles
--------------------

Recruiter
~~~~~~~~~

Persons responsible for invitations to studies and the management of appointments
should take on the role of **Recruiters** in Castellum. For this purpose, the
**Recruiter** can view the contact details of individual subjects to establish
communication with them. The **Study Coordinators** will define a recruitment
text to be clarified in advance, which the **recruiters** should use
when recruiting the respondent. To be able to schedule appointments, Castellum
provides a calendar which shows available time slots.

If a **Recruiter** additionally takes on the role of **Subject Manager**, they
can continuously update and supplement subject data during the recruitment
process.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`subject-edit`
-   :ref:`subject-report`
-   :ref:`recruitment`
-   :ref:`recruitment-mail`
-   :ref:`recruitment-appointments`
-   :ref:`scheduler-appointment`

Study Conductor
~~~~~~~~~~~~~~~

We envisage this role for employees from the study programme who collect
scientific data in a study with or on subjects. In order to implement this with
the help of Castellum, the **Study Conductor** can view the participation
pseudonyms of the respective subjects in the database.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`subject-edit`
-   :ref:`subject-report`
-   :ref:`subject-get-pseudonym`
-   :ref:`recruitment-appointments`
-   :ref:`scheduler-appointment`

.. TODO::

    -   attribute download
    -   make appointments

Overview
--------

.. figure:: /_images/groups.png
   :alt: Schematic overview of the default roles
