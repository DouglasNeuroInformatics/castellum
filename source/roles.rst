.. _roles:

Roles
=====

.. note::

    This section lists the roles that castellum ships by default. Administrators
    can customize these roles for their organization.

Study specific roles, in contrast to global ones, only take effect in the
context of a study. They can be assigned in **Member Management** by the
**Study Coordinator**.

Global roles
------------

Principal Subject Manager
~~~~~~~~~~~~~~~~~~~~~~~~~

The **Principal Subject Manager** enters data records of subjects in Castellum
and makes changes to existing ones.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`subject-create`
-   :ref:`subject-edit`
-   :ref:`subject-to-be-deleted`
-   :ref:`subject-consent`

Study Coordinator
~~~~~~~~~~~~~~~~~

The study coordination is embodied by the **Study Coordinator**. This person
inserts studies into the database and defines the settings for them.

Relevant guides:

-   :ref:`study-create`
-   :ref:`study-members`
-   :ref:`study-sessions`
-   :ref:`study-recruitment-settings`
-   :ref:`study-domains`
-   :ref:`study-finish`
-   :ref:`study-delete`
-   :ref:`set-up-external-scheduler`
-   :ref:`study-filter-trial`

Study Approver
~~~~~~~~~~~~~~

Study Coordinators by default cannot start their own studies. Instead, they
have to ask a **Study Approver** to review and start the study.

If you want to be less strict about this, you can either modify the Study
Coordinator role or make all Study Coordinators also Study Approvers.

Relevant guides:

-   :ref:`study-start`

Data Protection Coordinator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The group of people responsible for data protection should take on the role of
**Data Protection Coordinator**. Castellum supports these users by providing a
**data protection dashboard** that collects all relevant information in a
single place.

Relevant guides:

-   :ref:`data-protection-dashboard`
-   :ref:`subject-export`
-   :ref:`subject-delete`
-   :ref:`study-delete`

Receptionist
~~~~~~~~~~~~

We propose to fill the roles of **Receptionists** with people who need a
continuous overview of the ongoing study programme and the respective deadlines
in their daily business. In order to achieve this, these persons can search
specifically for names of subjects to be registered in Castellum. In this way it
is easy to find out for which study a particular subject is registered and when
they have to be sent to which room.

Administrator
~~~~~~~~~~~~~

**Administrators** are in charge of defining basic structures and performing
privileged actions.

Relevant guides:

-   :ref:`admin-users`
-   :ref:`admin-unlock`
-   :ref:`admin-roles`
-   :ref:`admin-attributes`
-   :ref:`admin-consent-document`

.. TODO::

    -   manage resources


Study specific roles
--------------------

Recruiter
~~~~~~~~~

Persons responsible for invitations to studies and the management of appointments
should take on the role of **Recruiters** in Castellum. For this purpose, the
**Recruiter** can view the contact details of individual subjects to establish
communication with them. The **Study Coordinators** will define a recruitment
text and criteria to be clarified in advance, which the **recruiters** should use
when recruiting the respondent. To be able to schedule appointments, Castellum
provides a calendar which shows available time slots.

If a **Recruiter** additionally takes on the role of **Subject Manager**, they
can continuously update and supplement subject data during the recruitment
process.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`recruitment`
-   :ref:`recruitment-mail`
-   :ref:`recruitment-appointments`
-   :ref:`make-appointments-with-external-scheduler`

Study Conductor
~~~~~~~~~~~~~~~

We envisage this role for employees from the study programme who collect
scientific data in a study with or on subjects. In order to implement this with
the help of Castellum, the **Study Conductor** can view the participation
pseudonyms of the respective subjects in the database.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`subject-get-pseudonym`
-   :ref:`make-appointments-with-external-scheduler`


.. TODO::

    -   attribute download
    -   make appointments

Subject Manager
~~~~~~~~~~~~~~~

**Recruiters** or **Study Conductors** may additionally be given this role so
they can update subject data as part of their usual workflows.

This role is different from **Principal Subject Manager** in that it is limited
to subjects that participate in the respective study.

Relevant guides:

-   :ref:`subject-search`
-   :ref:`subject-edit`
-   :ref:`subject-to-be-deleted`
