=================
Study recruitment
=================


.. _recruitment:

Recruit subjects via phone
==========================

.. figure:: /_images/recruitment-contact.png

1.  Click on **Studies** on the front page. Then click on **Execution** in the
    field **Status** to only show studies that are currently recruiting.

2.  Click on **Recruitment** next to the study you want to recruit subjects for

3.  By clicking on **Add**, relevant probands will be shown to you

4.  Press the **Contact** button to contact the person you want to reach

    -   **Email**, **Phone number**, a potential **Phone number alternative**
        and / or the **Address** will be shown to you in the tab **Contacting details**.

5.  Contact the potential subject using the specified method

    -   Please have a look at the **Talking points** that the study coordinator has
        provided

6.  When you received a response from the potential subject, select a **Status
    of participation**

    -   Choose between:

        -   **not reached**
            (Please note the appointment in the calendar)
        -   **follow-up scheduled**
            (Determine the date and time of the recall appointment below)
        -   **awaiting response**
            (This may apply if you left a message on the answering machine or if you
            sent an e-mail.)
        -   **participating**
        -   **excluded**
            (This may apply if recruitment attributes of the person do not comply with the
            requirements of the study, if a person is not interested in the
            particular study or if a person is not available during the data
            collection of the study)

    -   Click on **Save**


.. _recruitment-mail:

Recruit subjects via mail
=========================

.. note::

    Recruitment via mail is only possible if it has been :ref:`configured
    <study-recruitment-settings>` by the study coordinator.


1.  Click on **Studies** on the front page. Then click on **Execution** in the
    field **Status** to only show studies that are currently recruiting.

2.  Click on **Recruitment** next to the study you want to recruit subjects for

3.  Go to the **Mail** tab

4.  Enter the number of subjects that you want to contact

5.  Click **Send**

.. hint::
    The section **Previous mails** will appear after you have sent your first
    batch of mails. It lists all contacted groups allowing you to remind those
    potential participants of a group who did not respond yet. Please note, that
    this reminder can only be triggered once per group. It will send out the
    current invitation mail text with a prefixed e-mail subject indicating it as
    "Reminder/Erinnerung".

.. _recruitment-appointments:

Make appointments for sessions
==============================

.. note::

    This describes setting up appointments **for** the participants manually by
    Castellum users. There is also a guide on how to use the optional external
    scheduler feature in Castellum that offers potential participants to select
    appointments by themselves: :ref:`make-appointments-with-external-scheduler`.

If you are recruiting for a study that has at least one session Castellum allows
you to set up appointments for the participants:

1. In recruitment click on **Contact** in the *Open* list or on **Review** in the
   *Participating* list to get the details of the participant. Go to the tab
   **Appointments**.

2. The tab **Appointments** offers a date and time field for every session of
   the study. Click and populate those session fields that need to be appointed
   at this moment.

   .. hint::

       Study execution provides the same feature to make appointments with
       participating subjects. Thus, this can also be done by study conductors.

3. The **Calendar** button in the **Appointments** tab opens a new window and
   allows you to have a look at all already appointed sessions of the study.

.. warning::

    There are cases in which for example two subjects will be tested at the
    same time. For that reason castellum does not prevent you from booking
    overlapping appointments. You have to make sure that the requied staff and
    resources are available yourself.

.. _recruitment-cleanup:

Cleanup open list in recruitment
================================

The open list in study recruitment can become quite large and noisy if you are
waiting for many responses and/or failed to reach many potential participants.
Therefore, Castellum provides a cleanup feature:

1. Scroll down to the end of the open list in recruitment and click on
   **Cleanup**
2. Decide if you want to cleanup the *complete* open list (**All**) or
   only those potential participants whose status is marked as
   **Awaiting response** for more than 10 days. The third option allows you to
   run potentially modified recruitment filters on the list (**Mismatch**). This
   allows to cleanup those who do not match anymore. A click on either of these
   buttons will start the cleanup process.
3. After cleaning up the affected potential participants will be moved to the
   **Excluded** list with the additional tag **Excluded by cleanup**. This may
   allow you to reconsider contacting some of them.

The open list also gets quickly populated by mail recruitment (if set up) with
many potential participants with the status **Awaiting response**. Thus,
Castellum additionally allows to cleanup by mail batches:

1. Go to the **Mail** tab in recruitment and select an appropriate entry of the
   **Previous mails** list. Select **Cleanup**.
2. Confirm that you want to cleanup all potential participants of the mail batch
   who did not respond.
