Administration
==============

.. _admin-users:

Manage Users
------------

1.  Click on **Admin** on the front page
2.  Go to **Users**
3.  Click on **Add User** (oval with grey background)
4.  Enter the username and password and then click **Save and continue editing**

    .. warning::
        If you are using LDAP you should **not** enter a password.

5.  Add the appropriate global :ref:`roles`
6.  Add the appropriate :ref:`privacy-level`
7.  Add the appropriate **general pseudonym lists**
8.  Set an expiration date
9.  Click on one of the saving options


.. _admin-unlock:

Unlock locked Users
-------------------

There can be different reasons why a user has been locked:

1.  **Account has expired**: Update the expiration date (see :ref:`admin-users`)
2.  **Too many login attempts**: See `django-axes <https://django-axes.readthedocs.io/en/latest/3_usage.html#resetting-attempts-and-lockouts>`_
3.  **Lost access to second authentication factor**: Remove the user's MFA Keys via the admin interface


.. _admin-compromised:

Important steps when a user account has been compromised
--------------------------------------------------------

-   **Check the audit trail**: Castellum can be configured to create an
    :ref:`audit-trail` that sometimes allows to retrace suspicous behavior.
-   **Reset user tokens**: Besides login, some features of castellum can also
    be accessed by using a user token. An administrator can delete the token in
    the admin UI. A new one will be generated automatically.


.. _admin-roles:

Customize Roles
---------------

1.  Click on **Admin** on the front page
2.  Go to **Groups**
3.  Click on **Add Group** (oval with grey background)
4.  Enter a name for the new role
5.  Add the appropriate permissions (see the list of relevant :ref:`permissions`)
6.  Click on one of the saving options


.. _admin-attributes:

Manage Attributes
-----------------

Castellum does not dictate a fixed set of recruitment attributes that
can be stored. Instead, it allows to define your own attributes.

However, that flexibility comes with a cost: There are certain limits to
what you can define and migrating existing data is not that simple.

Create Attributes
~~~~~~~~~~~~~~~~~

1.  Click on **Admin** on the front page
2.  Go to **Attributes**
3.  Click on **Add attribute** (oval with grey background)
4.  Select an appropriate **Field type** that should be used for the attribute
5.  **URL** can be used to link to a formal definition. It is currently only
    used when exporting the attributes in BIDS format.
6.  **Order** and **Category** can be used to position the attribute in the UI
7.  **Statistics rank** allows to include this attribute in recruitment
    statistics. There can only be one of each, so you may have to deselect a
    primary or secondary attribute before selecting a new one.
8.  **Label** should be the actual name of the attribute.
9.  **Filter label** can be useful if you want to use a different label for the
    filter. Otherwise this can be left blank.
10. **Help text** can be used to provide additional hints to users.
11. If appropriate, fill in all possible values as **Attribute choices**. The
    options **Declined to answer** and **Unknown** are available by default, so
    there is no need to create them explicitly.
12. Be sure to provide translations for label, help text and choices if
    Castellum is set up to support more than one language

Change Attributes
~~~~~~~~~~~~~~~~~

While changing informational data such as label and help text is safe,
changing behavior (field type and choices) usually requires custom data
migrations. There is currently no special support for attribute
migrations in Castellum. However, it should be possible to create such a
migration using the available django interfaces.

As a general rule, we recommend creating a new Attribute and
deprecating the old one over modifying an existing one.

When you delete an attribute, all related data will automatically be
deleted along with it. Note that filters which use this attribute will
also be deleted.

Recommendations for Attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Though it may be tempting to store all kinds of meta data about subjects, you
should stick to a small set of attributes that you actuallt need for filtering.
Before adding one, you may want to consider the following check list:

-   Is the attribute needed for more than one study?
-   Do you have the ressources to gather and maintain this data?
-   Will the data stay relevant or will it change often?
-   Does the benefit of storing this data outweigh the risk for subjects in
    case of a data leak?


.. _admin-consent-document:

Upload a consent document
-------------------------

Upload a new document
~~~~~~~~~~~~~~~~~~~~~

1.  Click on **Admin** on the front page
2.  Go to **Consent documents**
3.  Click on **Add Consent Document** (oval with grey background)
4.  Choose the file you want to upload
5.  Click on one of the saving options

Now whenever consent is added to a subject, the user can pick this new version
from a list of all available documents.

Deal with the old document
~~~~~~~~~~~~~~~~~~~~~~~~~~

If there have been significant changes to the document, the old version may no
longer be a sufficient legal basis to keep subjects in the database. In that
case there is a two step process:

1.  Mark the old consent document as **deprecated**. The document is still
    considered valid but subjects who have agreed to this document will show up
    in the consent maintenance view (see below).
2.  Mark the old consent document as **not valid**. Now all consents related to
    this document are void. Subjects who have not been updated to another
    document are no longer available for recruitment and will potentially show
    up in the data protection dashboard.

The legal basis for each subject can be found in the subject detail view.


.. _admin-general-pseudonym-lists:

Manage general pseudonym lists
------------------------------

1.  Click on **Admin** on the front page
2.  Go to **Domains**
3.  Click on **Add Domain** (oval with grey background)
4.  Enter a name
5.  Leave the ``object_id`` and ``content_type`` fields empty
6.  Click on one of the saving options


.. _admin-resources:

Manage resources
----------------

A resource is something that is needed in an appoitnemnt, e.g. a room or a
device. If you set up resources, study coordinators can select which of those
resources are required for their sessions. The main benefit is that you can
then get a calendar with all appointments that are associated with this
resource.

To set up a resource:

1.  Click on **Admin** on the front page
2.  Go to **Resources**
3.  Click on **Add Resouce** (oval with grey background)
4.  Enter a **name**
5.  Select which users should have **access** to the resource calendar
6.  If relevant, you can include an **external calendar** (ics) that contains
    additional events, e.g. if the resource can be blocked for reasons other
    than participant appointments.
7.  The last option allows you to select a **color** for the external calendar
    events.
8.  Click on one of the saving options
