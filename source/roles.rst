.. _roles:

Roles
=====

.. NOTE::

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

-   :ref:`subject-create`
-   :ref:`subject-to-be-deleted`
-   :ref:`consent`

.. TODO::

    -   Search for individual subjects in the database
    -   See, add and edit contact data and attributes ob individual subjects

Study Coordinator
~~~~~~~~~~~~~~~~~

The study coordination is embodied by the **Study Coordinator**. This person
inserts studies into the database and defines the settings for them.

Relevant guides:

-   :ref:`study-create`
-   :ref:`study-members`
-   :ref:`study-recruitment-settings`
-   :ref:`study-finish`
-   :ref:`study-delete`

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

The group of people who deal with data protection issues in the workplace should
take on the role of **Data Protection Coordinator** in Castellum. Technically,
Castellum provides a Data Protection Dashboard for this purpose. In this
dashboard, the **Data Protection Coordinator** can see subjects divided into
four categories:

-   Subjects that requested information regarding their personal data,
-   Subjects that have been marked as **To be deleted**

    -   This applies when a subject demanded a deletion of all scientific data
        related to them.
    -   The **Data Protection Coordinator** can see all studies the subject
        participated in. He will contact all **Principal Investigators** and demand
        the deletion of collected study data (provided that these are still
        attributable to the respective subject).
    -   Once all links to studies have been removed, the subject can be deleted
        from the database.

-   Subjects for whom there is no (or no longer any) legal basis for keeping
    them in the database and
-   Subjects who cannot be contacted due to missing or wrong information regarding
    their contact details.

The **Data Protection Coordinator** has the task of cleaning up the dashboard by
initiating follow-up steps for each category.
To initiate such follow-up actions, the **Data Protection Coordinator** is enabled
to perform the following functions in the database:

Relevant guides:

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

Relevant guides:

-   :ref:`admin-users`
-   :ref:`admin-roles`
-   :ref:`consent`

.. TODO::

    -   manage resources
    -   manage attribute descriptions


Study specific roles
--------------------

Recruiter
~~~~~~~~~

Persons responsible for invitations to studies and the management of appointments
should take on the role of **Recruiters** in Castellum. For this purpose, the
**Recruiter** can view the contact details of individual subjects to establish
communication with them. The study co-ordination office will define a recruitment
text and criteria to be clarified in advance, which the **recruiters** should use
when recruiting the respondent. To be able to add study participations, Castellum
provides a calendar which enables consistent appointment bookings.

If persons take on the role of **Recruiter** and additionally **Subject Manager**,
they can simultaneously ensure data maintenance in Castellum when contacting
subjects for recruitment purposes. For this purpose, characteristics and contact
details of subjects are continuously updated and supplemented.

Relevant guides:

-   :ref:`recruitment`

.. TODO::

    -   mail recruitment
    -   make appointments

Study Conductor
~~~~~~~~~~~~~~~

We envisage this role for employees from the study programme who collect
scientific data in a study with or on subjects. In order to implement this with
the help of Castellum, the **Study Conductor** can view the participation
pseudonyms of the respective subjects in the database.

If a subject is participating in a study for the first time, the **Study
Conductor** can obtain both the study consent and the recruitment consent on site.

Relevant guides:

.. TODO::

    -   get a subject's pseudonym
    -   attribute download
    -   make appointments

Subject Manager
~~~~~~~~~~~~~~~

**Recruiters** or **Study Conductors** may be given this role so they can
update subject data as part of their usual worflows.

This role is different from **Principal Subject Manager** in that it is limited
to subjects that participate in the respective study.

Relevant guides:

-   :ref:`subject-to-be-deleted`
