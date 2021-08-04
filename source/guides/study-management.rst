.. _study-create:

Create a study
==============

1.  Click on **Create new study**

2.  Fill in all required fields on the page:

    -   **Name** describes the title of the study you want to create
    -   **Responsible contact person** is the person who can be contacted if
        any questions regarding the study occur
    -   **Principal Investigator** is the lead researcher
    -   **Phone number** and **E-mail-address** are the contact information at
        which the contact person can be reached

3.  Decide on setting it up as a regular study that includes study recruitment
    and execution or as a **one time invitation**. The option **Is a one time
    invitation** should only be used when you are sure that it is sufficient to
    invite potential subjects **anonymously** via mail.

4.  Fill in any additional information (you can still do that later)

5.  Click on **Save** to record your progress

.. warning::
    When choosing option **Is a one time invitation**: Please be aware that
    Castellum will **not** track actual participations or appointments and it
    will **not** provide pseudonyms within the study.

Now you can :ref:`find your study <study-search>` in the studies list.


.. _study-sessions:

Set up sessions
---------------

In the **Sessions** tab, you can enter as many test sessions as you like.

-   **Add session**
-   Set up **Start of test sessions** and **End of test sessions**
-   Define general **Session instructions**

.. note::
    In **Session Instructions** you can inform recruiters on
    conditions/requirements that may be important for or in between sessions.
    For example, recruiters are often asked to ensure a certain time interval
    between session appointments. This would be explained here.

    **Start** and **End of test sessions** allows Castellum to offer an
    approximate overview schedule of all studies in Calendar view at Study
    management.

When adding a test session:

-   Always give the session a **Name** and specify the **Duration of a session
    in minutes** (duration will be used for appointment booking)
-   Additionally, select the **Type** of the session and (if applicable at your
    institute) select a **Ressource**
-   **Additional text for reminder emails** allows you to provide information
    to subjects prior to the actual appointment. You can send yourself a test
    mail to check the appearance of session reminders by using the
    corresponding button
-   If your institute uses the external scheduler to schedule appointments, you
    can enable it here  (see :ref:`set-up-external-scheduler`)

For existing sessions a **Delete** button allows you to delete any test session
you created. Click on **Update** to review or edit session details.


.. _study-recruitment-settings:

Set up the recruitment process
------------------------------

Castellum offers three features to restrict which subjects are considered for
your study:

-   Attribute filters
-   Excluded studies
-   Text based inclusion and exclusion criteria

.. note::

    At first it may be unclear how to distinguish **attribute filters** and
    **inclusion/exclusion criteria**:

    -   Attribute filters are applied to subject attributes stored in
        Castellum. In other words, this will only suggest matching potential
        subjects in recruitment.
    -   Inclusion and exclusion criteria need to be used when there is no data
        available about it in Castellum. Therefore, they must be checked by a
        staff member explicitly during recruitment.

1.  Go to the **Recruitment Settings** tab

2.  By clicking on **General** the **Recruitment text** will be shown to you.
    You can:

    -   edit the **Recruitment text** (this text will be shown to recruiters
        and will be used by them to recruit subjects for your study),
    -   decide whether you wish to set up the **Advanced filtering** (this
        allows you to create multiple filtergroups that are not linked to each
        other),
    -   set the function **Exclusive subjects** (If you select this feature,
        potential subjects for your study cannot be recruited for other
        studies. Please note that this may prevent other researchers from
        finding enough participants.) and
    -   decide whether **Complete filter matches only** will be shown to the
        recruiters of your study or if there will be some subjects displayed,
        in which certain characteristics still have to be queried

3.  By clicking on **Filter** you are able to set filter criteria

    -   select the attribute that should be used for filtering
    -   click **Add**
    -   define the filter
    -   click **Apply**

    You may set as many filters as you like.

    .. note::
        Please note that **all filter criteria** set up within this filter
        group have to be **fulfilled**. This also means that opposing filters
        would result in an empty set.

    Sometimes you need to define more than one mutually exclusive group of
    suitable subjects. For this, you have to set up **advanced filtering** in
    general recruitment settings to create various filter groups.

    Subsequently, when you click on **Add new** in **Filters**, you are able to
    set another filter group with specific filters. Alternatively, you could
    duplicate an existing filter group and edit it afterwards.

    .. admonition:: Example

        This is necessary if you need subjects both at the age between 20-30
        and 50-60. Again, note the distinction between **Any of these** and
        **All of these**.

4.  In **Excluded studies** you can select certain studies in which your
    subjects must not have participated

5.  When you click on **Inclusion/exclusion criteria**, you can add
    **additional subject characteristics that should be verified during the
    recruitment**

    .. note::

        Session types may come with specific criteria that have to be checked
        every time before appointing subjects to a session. In this case,
        you'll see a caret with a label **Criteria for: <type>** next to the
        text field. Clicking on it will show you the text that is always
        appended. In other words: You don't have to write this type specific
        text by yourself.

6.  To allow recruiters to send batch invitations via e-mail, proceed as
    follows:

    -   click on **Mail Settings**
    -   define an **E-mail subject**
    -   add an **E-mail body**

    This e-mail will be sent by recruiters at study recruitment by specifying
    the amount of recipients. Yet, you can check the appearance of the set up
    mail by sending a test mail to yourself with corresponding button.

    .. note::

        It is not intended to send e-mail attachments via Castellum. Instead,
        links can be inserted as standard text.


.. _study-domains:

Manage study pseudony domains
-----------------------------

In the **Pseudonym domains** tab you can add a new domain or change the name of
an existing domain.

If there are general domains you can also define which general domains need to
be accessed in the context of this study.


.. _study-members:

Manage study members
--------------------

If you want to give access to other staff members (e.g. recruiters) for your
study, please follow the steps below.

1.  Go to the **Member management** tab

2.  If you click on the field under **User**, you will be shown all possible
    users to whom you can assign roles

3.  Select the user who is supposed to take over the recruitment

4.  Click on **Add**

5.  Click **Manage groups** next to the person you have chosen

6.  Select the appropriate roles and click **Save**

    .. note::

        Some features (e.g. recruitment) only become available once the study
        is started. So, some added users may not instantly notice those role
        changes.


.. _study-start:

Start and stop a study
======================

After a study has been created it is still in a draft state. Only Study
Approvers have the permission to start recruitment. Depending on your
organization, there may be different organizational steps such as a review
associated with that.

In order to start or stop a study, a Study Approver needs to follow these
steps:

1.  :ref:`Find the study <study-search>` at the **Studies** page, click
    **Details** next to the study you wish to start/stop

2.  You can find the button **Start** near to the study name. By clicking on
    **Start** you initiate the recruiting process. Started studies will offer a
    stop button instead to stop (or pause) recruitment.

.. warning::

    A study can still be changed after it has been approved and started. The
    tab "Changes" provides an overview of all the settings for a study. Any
    changes that were made since the study was started are highlighted.


.. _study-finish:

Finish a study
==============

1.  :ref:`Find the study <study-search>` at the **Studies** page, click
    **Details** next to the study you wish to finish/resume.

2.  You can find the button **Finish study** next to the study name near to
    other buttons.

.. note::

    All information related to potential subjects who were **not participating** in
    the study will be deleted when the study is finished. Hence, if you finish
    and then resume a study, it is possible that subjects that were already
    found to be unsuitable are suggested again as potential subjects.


.. _study-delete:

Delete a study
==============

When a study should be deleted depends on the rules of your specific
organization. We assume that it makes sense to delete all study data after few
years, effectively anonymizing the research data.

Once you delete a study from Castellum it is no longer possible to answer to
export or delete requests from subjects. Make sure that all relevant external
has been deleted before you delete a study from Castellum. Then proceed as
follows:

1.  :ref:`Find the study <study-search>` at the **Studies** page, click
    **Details**

2.  Make sure the study is finished (see :ref:`study-finish`)

3.  Click on **Delete** under the study name. Confirm the notice **I have made
    sure that all external data related to this study has been destroyed** by
    clicking on **Confirm**


.. _study-search:

Find your study
===============

Click on **Studies** on the front page

-   By selecting **Mine** in **Membership**, you will see studies you created
    or are a member of. Under the field **All** you can see all studies that
    have been created.
-   In the field **Search** you can look for a certain study
-   By choosing a **Status** and / or a Study **Type**, you may also filter
    studies
