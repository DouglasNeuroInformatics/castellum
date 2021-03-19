.. _admin-users:

Manage Users
============

1.  Click on **Admin** on the front page
2.  Go to **Users**
3.  Click on **Add User** (oval with grey background)
4.  Enter the username and password and then click **Save and continue editing**

    .. warning::
        If you are using LDAP you should **not** enter a password.

5.  Add the appropriate global :ref:`roles`
6.  Add the appropriate :ref:`privacy-level`
7.  Set an expiration date
8.  Click on one of the saving options


.. _admin-unlock:

Unlock locked Users
===================

There can be different reasons why a user has been locked:

1.  **Account has expired**: Update the expiration date (see :ref:`admin-users`)
2.  **Too many login attempts**: See `djang-axes <https://django-axes.readthedocs.io/en/latest/3_usage.html#resetting-attempts-and-lockouts>`_


.. _admin-roles:

Customize Roles
===============

1.  Click on **Admin** on the front page
2.  Go to **Groups**
3.  Click on **Add Group** (oval with grey background)
4.  Enter a name for the new role
5.  Add the appropriate permissions (see the list of relevant :ref:`permissions`)
6.  Click on one of the saving options


.. _admin-attributes:

Add Attribute Descriptions
==========================

Castellum allows to dynamically add attribute descriptions that can be used to
store filterable information on subjects. This takes into account that there are
only very few attributes that can be seen as commonly used at every institute.


.. _admin-consent-document:

Upload a consent document
=========================

Upload a new document
---------------------

1.  Click on **Admin** on the front page
2.  Go to **Consent documents**
3.  Click on **Add Consent Document** (oval with grey background)
4.  Choose the file you want to upload
5.  Click on one of the saving options

Now whenever consent is added to a subject, it implicitly refers to this new
version.

Deal with the old document
--------------------------

If there have been significant changes to the document, the old version may no
longer be a sufficient legal basis to keep subjects in the database. In that
case there is a two step process:

1.  Mark the old consent document as **deprecated**. The document is still
    considered valid but subjects who have agreed to this document will show up
    in the consent maintenance view (see below).
2.  Mark the old consent document as **invalid**. Now all consents related to
    this document are void. Subjects who have not been updated to the new
    document are no longer available for recruitment and will potentially show
    up in the data protection dashboard.

The legal basis for each subject can be found in the subject detail view.
