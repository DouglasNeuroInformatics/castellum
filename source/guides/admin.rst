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
