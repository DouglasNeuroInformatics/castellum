==============
Administration
==============

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
7.  Add the appropriate **general domains**
8.  Set an expiration date
9.  Click on one of the saving options


.. _admin-unlock:

Unlock locked Users
===================

There can be different reasons why a user has been locked:

1.  **Account has expired**: Update the expiration date (see :ref:`admin-users`)
2.  **Too many login attempts**: See `djang-axes <https://django-axes.readthedocs.io/en/latest/3_usage.html#resetting-attempts-and-lockouts>`_
3.  **Lost access to second authentication factor**: Remove the user's MFA Keys via the admin interface


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

1.  Click on **Admin** on the front page
2.  Go to **Attribute description**
3.  Click on **Add attribute description** (oval with grey background)
4.  Select an appropriate **Field type** that should be used for the attribute
5.  **URL** allows you to link to a formal definition that may clarify baseline
    or rather scientific grounding of the attribute

    .. note::
        This is used to support Recruitment Attribute Export in BIDS format. Hence, it is
        only shown in admin interface. For example, a Handedness attribute could
        link to a definition at
        `bioontology.org <http://purl.bioontology.org/ontology/SNOMEDCT/57427004>`_.

6.  Set **privacy levels** of the attribute for **read** and **write**
7.  **Order** and **Category** can be used to position the attribute in UI
8.  **Statistics rank** can be used to set this attribute as primary or
    secondary feature that should be presented in statistics of recruitment

    .. note::
        Castellum offers to set up two attributes to be used in statistics of
        recruitment. If there is already a primary or secondary attribute it
        will show an error warning. Accordingly, you have to deselect a primary
        or secondary attribute first to select a new one.

9.  **Label** should be the actual name of the attribute. Be sure to provide
    translations if Castellum is set to support more than one language
10. If appropriate, fill in all **Attribute choices** (if needed also add
    translations) that represent the possible values of the attribute and will
    be used for filtering

    .. note::
        Attributes will always allow to select **Declined to answer**. So, there
        is no need to specify this as an attribute choice. Furthermore, all
        three ChoiceField types will automatically provide an **Unknown**
        option.


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


.. _admin-general-domains:

Manage general domains
----------------------

1.  Click on **Admin** on the front page
2.  Go to **Domains**
3.  Click on **Add Domain** (oval with grey background)
4.  Enter a name
5.  Leave the ``object_id`` and ``content_type`` fields empty
6.  Click on one of the saving options
