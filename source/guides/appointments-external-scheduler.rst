.. _set-up-external-scheduler:

Set up an external scheduler for appointments
=============================================

Castellum allows the use of an external scheduler. That way subjects can select
the dates for appointments for study sessions themselves.

.. note::
   Note that this is an optional feature which may not be activated in your setup.
   If the links referenced in this guide are missing from the user interface, the
   feature is not installed. If you would like to use it, please talk to the
   administrator of your castellum instance.

1.  Find the scheduler link in castellum

    -   On the startpage, click **Studies**.
    -   In the studies list, select a study by clicking **Details**.
    -   Go to the **Sessions** tab.
    -   If there are no sessions yet, create some:
        :ref:`study-recruitment-settings`
    -   Next to a session, click **Update**.
    -   Click **New schedule**.

2.  Create a new schedule in the scheduler

    -   On the startpage, click **Create new**.
    -   Add a meaningful title such as the name of the session this schedule
        refers to.
    -   Under "Timeslots", add all dates on which appointments are available
        and each time confirm with **Add date**. The format depends on your browser
        settings. Each date will add a new row to the table below.
    -   On the next line, add all times on which appointments are available and
        each time confirm with **Add time**. The format depends on your browser
        settings. Each date will add a new column to the table below.
    -   Clicking on the checkboxes allows to deactivate individual slots for
        refinement.
    -   Clicking on the bin symbol removes the entire row or column.
    -   Confirm your selection by clicking **Save**.
    -   Note the ID of this schedule. It's the last number of the URL (e.g.
        "yourscheduler/3/"). You will need it in the next step.

3.  Enter the schedule id in castellum

    -   Under **External schedule ID**, enter the scheduler ID.
    -   Confirm with **Save**.
    -   The scheduler can now be used in recruitment.


.. _make-appointments-with-external-scheduler:

Make appointments with the external scheduler
=============================================

Castellum allows the use of an external scheduler. That way subjects can select
the dates for appointments for study sessions themselves.

.. note::
   Note that this is an optional feature which may not be activated in your setup.
   If the links referenced in this guide are missing from the user interface, the
   feature is either not installed or not used for this session. If you would like
   to use it, ask the study coordinator for this study to enable it.

1. Navigate to the scheduler link

    -   in the subject details (step for of this guide: :ref:`recruitment`),
        in recruitment, click **Appointments**.
    -   Click **Select timeslot for this subject** to go to the scheduler.
        Clicking the "Copy" symbol will copy the scheduler link to your clipboard
        so you can send it to the subject via email.

2.  In the scheduler, select an appointment and click **Save**. This step can
    also be done by the subject themself (if you've sent them the link).
