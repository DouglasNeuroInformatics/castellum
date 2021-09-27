==========================
Data protection: workflows
==========================


.. _data-protection-dashboard:

Use the data protection dashboard
=================================

Click on **Data protection** on the front page to go to the data protection
dashboard. This dashboard lists tasks you need to take care of by initiating
follow-up steps for each category.

-   **Export requested** lists all subjects who requested a GDPR export. See
    :ref:`subject-export` for the necessary steps.
-   **To be deleted**, **No legal basis**, and **Unreachable** all list
    subjects who should be deleted for different reasons. See
    :ref:`subject-delete` for the necessary steps.

In all those categories it usually makes sense to contact the subjects before
taking any action. For example, subjects often want only a part of their data
deleted.

Most of the categories have legal time limits, so you should check the
dashboard regularly.

.. hint::

    It is recommended to configure an email address that should receive email
    notifications about new data protection tasks. Please ask your system
    administrator to setup ``CASTELLUM_GDPR_NOTIFICATION_TO``.


.. _subject-export:

Export all data related to a subject
====================================

According to GDPR, subjects have the right to get an export of all their data.
This is especially important for scientific measurements that need to be
provided in a common file format. Compared to that, the data stored in
castellum is rather simple (e.g. name and address). Still, it is possible to
generate a complete list of all the information that is stored in castellum on
a single subject.

1.  In the subject details, go to the **Export** tab

2.  If you see a message saying **No export requested**, you need to
    explicitly **Request export**. The date of the request will be stored.

3.  The complete list can be printed or otherwise stored.

4.  Once the subject has received the export, click **Mark as answered** to
    record how long it took to process this request.

.. warning::

    These steps only outline the data export from a software view. Your institute should provide organizational steps
    to verify actual identity of the requester. Furthermore, secure transfer of exported data needs to be set up.