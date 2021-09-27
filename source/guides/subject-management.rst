==================
Subject management
==================


.. _subject-search:

Search for a subject
====================

.. figure:: /_images/subject-search.png

1.  Click on **Subjects** on the front page

2.  Enter the first name and surname, the email address, or the phone number

    -   The second first name can be specified, but does not have to be
    -   Keep the order as indicated
    -   No comma needed

3.  Confirm by clicking **Submit**

4.  Under the **Matches** tab all matching subjects or their legal
    representatives are listed

    -   Next to their name the date of birth is listed and, if provided, also
        their email address
    -   If either parts of their name or their email address are matched
        exactly by your search terms, this part is highlighted in yellow
    -   **Details** will take you to the subject overview page
    -   If a subject has any study participations, they are listed below in
        this order: name of the study, the name of the responsible contact
        person and the participation status. The buttons **Recruitment** and
        **Execution** (if the study is still in execution) lead to recruitment
        and execution for this study. Note that whether you can see study
        participations is dependent on your permissions

5.  If there is a **Match** found, confirm that this is the correct person by
    asking for a second feature (e.g. date of birth).

    .. warning::
        Only ask for a second feature, do not disclose any information
        yourself. This is to avoid leaking personal information to imposters.


.. _subject-create:

Create a subject
================

Subject data is split up into subsets that include at least the following
information:

-   **First name** and **Last name**
-   **Gender**
-   **Date of birth**
-   Information on whether the person is **Full of age** or **has legal
    representative**. If the subject has a legal representative, you will need
    to **Add legal representative** (see instructions in
    :ref:`subject-contact-tab`)
-   **E-mail** address and/or **Phone number** and/or full postal address
    and/or contacting details of the legal representative
-   **Recruitment attributes**
-   **Interest in study types**
-   **Privacy level**
-   **Recruitment Consent** given
-   **GDPR requests**
-   **Study Participations**

In order to create a potential subject in Castellum, please proceed as follows:

1.  :ref:`subject-search`

    1.  If there is a **Match** found, the subject is already created in the
        database. You may edit or add information to this subject by clicking
        on **Details** next to the subject. If it turns out that a **Match** is
        a different person with the same name you are free to create a new
        subject.

    2.  If **No matches can be found**, click on **Create**. If you notice that
        you made a spelling mistake with the names, please do not go back and
        create the person again, but change the name in the following process.

2.  Define the **Privacy level**

    -   0 (regular) describes adults without extraordinary features
    -   1 (increased) indicates children or adults with a legal representative
    -   2 (high) represents adults (and their children/wards) who for example
        are public figures

3.  Click on **Create new subject**

.. warning::

    Recruiters often find themselves in fast paced situations when talking to
    new potential subjects. Hence, we decided to support a quick creation of
    subjects. Therefore, a subject is initially created with **very basic**
    information on name and privacy level. To assure a *viable* data set there
    is much more information you should enter (see :ref:`subject-edit`).

.. _subject-edit:

Edit Subject Data
=================

Subject data consists of several subsets represented as tabs. Tabs that lack
some important information are highlighted by an icon with an exclamation mark.
Below, you'll find a short description for each tab. Please note that tabs need
to be saved upon changes individually.

.. figure:: /_images/subject-tabs.png

.. _subject-overview-tab:

Overview Tab
------------

This tab gives you a quick overview of the subject data. Importantly, it offers
different legal bases for storing the subject data in Castellum. You can check,
add or rather edit the consent that applies:

-   **Recruitment consent**
-   **Study consent**
-   **Legal representative**
-   **Subject blocked**

.. _subject-contact-tab:

Contact Tab
-----------

This tab allows you to set up common information needed to get into contact
with a subject.

-   Optionally you can enter the **Title** here
-   You can edit the **First name** and **Last name**
-   Define the **Gender** of the person
-   Fill in the **Date of birth**

1.  If the person is an adult, select **Full of age** and continue with
    the following steps:

    -   Define at least one of the following contact details: **Email**, **Phone
        number** and/or **Postal address**
    -   You may want to add **Additional information** for postal address, such
        as c/o details
    -   Specify the **Preferred contact method**

2.  If the person is not of an adult age or has a legal representative for
    example due to a disability or illness, select **Has legal representative**
    > **Add legal representative**

    -   A new window will open
    -   Fill in the first and last name of the subject's legal representative >
        **Submit**
    -   If a **Match** is found, select it
    -   If **No matches found** applies, click **Create** > Enter necessary
        information in the fields provided > **Create new subject**

    .. note::
        The legal representative is now added. You can also create several
        legal representatives. By clicking on **Remove** next to the legal
        representative's name, you can delete them as the legal representative
        of the subject.

.. _subject-attributes-tab:

Recruitment Attributes Tab
--------------------------

The recruitment attributes tab lists all attributes and interests in study types.
Recruitment attributes are features that are used to decide on suitability for a
study. It is expected that they only provide *indications* on suitability as
there are usually additional criteria that need to be checked for a study
match.

-   Fill in the recruitment attribute fields used at your institute
-   If the person **Does not want to participate in the following study types**,
    select one or more

.. admonition:: Example

    Recruitment attributes may be **Mother Tongue**, **Highest Educational Degree**,
    **Age**, **Handedness** and so on.

.. _subject-data-protection-tab:

Data Protection Tab
-------------------

At the data protection tab should be used for to document recruitment consent
and GDPR requests.

-   redefine the **Privacy level**
-   indicate whether the subject has consented to the recruitment (for details
    see :ref:`subject-consent`)
-   initiate an **Export request**
-   specify whether the subject is **To be deleted**

.. _subject-info-tab:

Additional Info Tab
-------------------

This tab mainly focusses on when to best reach out to subjects.

-   define the **Availability** of the subject

    .. admonition:: Example

        The person is abroad for 6 months.

        -   Select **Not available until** today in 6 months

-   define which **Data source** the data comes from

.. _subject-participations-tab:

Study Participations Tab
------------------------

The participations tab is offering to check existing participation or add the
current subject to a study

-   **Participating**: Lists the study participations of this subject
-   **Matching Studies**: A list of currently active studies with matching
    filters is displayed. You can add the subject to one or more study
    recruitments.
-   **Add to study**: Search for a study and add the subject
    directly as *participating* to it.

.. _subject-to-be-deleted:

Mark a subject for deletion
===========================

To satisfy GDPR requests for deletion of all data related to a subject, please
proceed as follows:

1.  Click on **Subjects** on the front page

2.  Enter the first name and surname of the subject to be deleted into the
    search field and click on **Submit**

3.  Click on **Details** and then go to the **Data protection** tab

4.  Select the checkbox **To be deleted**

5.  Click on **Save**

The subject is now cleared for deletion from the database and deletion of
their associated data. The data protection coordinator will take care of final
deletion.


.. _subject-delete:

Delete a subject
================

You may want personal data and subjects to be completely deleted because of an
explicit request from the subject or simply because there no longer is a
sufficient legal basis to keep the data.

.. note::

    This is only available for users with permissions that are granted to staff
    members who are data protection coordinators or the like.

    If deletion was requested by a subject you should follow your institute's
    rules on verifying identity of requester.

In order to delete the externally and internally stored data of a subject,
please proceed as follows:

1.  In the subject details, go to the **Delete** tab

2.  If you see a message saying **This subject cannot be deleted because there
    still is data about them in studies.**, proceed as follows:

    -   Contact the responsible person for each study and ask them to delete
        all collected data of the subject concerned. Identify the subject using
        the study pseudonym that is displayed.
    -   Once the responsible contact person has confirmed the deletion of all
        data, delete the participation record using the **Delete** button.

3.  If you see a message saying **This subject may still have data in general
    domains.**, proceed as follows:

    -   Click on **Pseudonyms** next to **General pseudonym domains** to get a
        list of pseudonyms.
    -   Contact the responsible person for each general domain and make sure
        that all data is deleted.

4.  Once all participations have been deleted you will see a message saying
    **Are you sure you want to permanently delete this subject and all related
    data?** You can now click **Confirm** and the subject will be deleted.

.. warning::

    There may still be data stored in a backup. Please check with your local IT
    department to verify proper deletion.

.. note::

    Deleting a subject who has legal representatives will **not** automatically
    delete the corresponding legal representatives. However, if there is no
    other reason to keep the legal representatives in Castellum, they will
    appear in the data protection dashboard.
