Study management
================


.. _study-create:

Create a study
--------------

1.  Click on **Create new study**

2.  Fill in all required fields on the page:

    -   **Name** describes the title of the study you want to create
    -   **Principal Investigator** is the lead researcher
    -   **Responsible contact person** is the person who can be contacted if
        any questions regarding the study occur
    -   **Phone number** and **Email-address** are the contact information at
        which the contact person can be reached
    -   **Required number of subjects** is the number of people you need to
        recruit for this study

3.  Decide on setting it up as a regular study that includes study recruitment
    and execution or as a **one time invitation**. The option **Is a one time
    invitation** should only be used when you are sure that it is sufficient to
    invite potential subjects **anonymously** via mail.

4.  Fill in any additional information (you can still do that later)

    .. note::

        Quick note on **Consent**: this allows users to upload a blueprint of
        the study consent. This blueprint can be obtained (and printed) later by
        recruiters or conductors.

5.  Click on **Save** to record your progress

.. warning::
    When choosing option **Is a one time invitation**: Please be aware that
    Castellum will **not** track actual participations or appointments and it
    will **not** provide pseudonyms within the study.


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
    institute) select **Resources**
-   **Additional text for reminder emails** allows you to provide information
    to subjects prior to the actual appointment. You can send yourself a test
    mail to check the appearance of session reminders by using the
    corresponding button
-   If your institute uses the external scheduler to schedule appointments, you
    can enable it here (see :ref:`scheduler-setup`)

For existing sessions a **Delete** button allows you to delete any test session
you created. Click on **Update** to review or edit session details.


.. _study-recruitment-settings:

Set up the recruitment process
------------------------------

Castellum offers three features to restrict which subjects are considered for
your study:

-   Attribute filters
-   Excluded studies
-   Text based inclusion and exclusion criteria as part of the recruitment text

1.  Go to the **Recruitment Settings** tab

2.  By default you will see the **General** recruiment settings:

    -   The **Recruitment text** will be shown to recruiters and will be used
        by them to recruit subjects for your study. Use this for any criteria
        that have to be checked manually.
    -   Decide whether you want to use **advanced filtering**. This
        allows you to set up multiple filter groups. Subjects will be
        considered for the study if they match any of those groups.
    -   Decide whether you want to use **exclusive subjects**. If you enable
        this option, potential subjects for your study cannot be recruited for
        other studies. Please note that this may prevent other researchers from
        finding enough participants.
    -   Decide whether you want to restrict your recruitment to **complete
        filter matches only**. This excludes subjects with unknown attributes.
        It is recommended to leave this off and try to complete the missing
        attributes, both to improve the database and to increase the pool of
        potential subjects.
    -   You can restrict subjects based on a **maximum number of reliability
        issues** to filter out unreliable subjects.
    -   You can restrict subjects based on **last activity**, e.g. to
        prioritize subjects who have recent experience with your organization.

    .. note::
        Session types may come with specific criteria that have to be checked
        every time before appointing subjects to a session. In this case,
        you'll see a caret with a label **Criteria for: <type>** next to the
        recruitment text. Clicking on it will show you the text that is always
        appended. In other words: You don't have to write this type specific
        text by yourself.

3.  By clicking on **Filter** you are able to set filter criteria

    -   select the attribute that should be used for filtering
    -   click **Add**
    -   define the filter
    -   click **Apply**

    You may set as many filters as you like.

    Sometimes you need to define more than one group of suitable subjects (e.g.
    age 20-30 and age 50-60). For this, you have to activate **advanced
    filtering** in the general recruitment settings (see above).

4.  In **Other studies** you can select certain studies in which your
    subjects must or must not have participated

5.  To allow recruiters to send batch invitations via email, proceed as
    follows:

    -   click on **Mail Settings**
    -   define an **Email subject**
    -   add an **Email body**

    This email will be sent by recruiters at study recruitment by specifying
    the amount of recipients. Yet, you can check the appearance of the set up
    mail by sending a test mail to yourself with corresponding button.

    .. note::

        It is not intended to send email attachments via Castellum. Instead,
        links can be inserted as standard text.

Create a geo filter
~~~~~~~~~~~~~~~~~~~

If that feature has been activated on the server, Castellum also allows to
filter by geographical properties of a subject's address.

.. admonition:: Example

    If the desired participants for a study should be older than 40 years
    and live in an area where the noise from an airport is over 40dB you
    would create and upload a GeoJSON file with a (multi)polygon spanning
    the area where this condition applies. Afterwards proceed as usual with
    setting the filter for age in the study filter UI. The resulting
    subjects in the recruitment interface match the filter condition AND
    their contact address is located inside the uploaded polygon.

GeoJSON format
``````````````

To use this, you need to provide a valid `GeoJSON
<https://tools.ietf.org/html/rfc7946>`__ file with a either a single feature or
a feature collection of type “Polygon” or “MultiPolygon”. Castellum will then
filter all subjects that live inside this (multi)polygon, so it should enclose
all areas where the conditions for recruitment are met. Note that the
Coordinate Reference System (CRS) must be WGS84 (EPSG:4326).

This is an example of a valid GeoJSON file::

   {
     "type": "Feature",
     "properties": {},
     "geometry": {
       "type": "Polygon",
       "coordinates": [[
         [13.3517429, 52.5189382],
         [13.2908489, 52.5165476],
         [13.3463410, 52.4848593],
         [13.3512518, 52.4468630],
         [13.3964313, 52.4785787],
         [13.4627272, 52.4504546],
         [13.4308069, 52.4893448],
         [13.4730399, 52.5192370],
         [13.4141102, 52.5180417],
         [13.3821899, 52.5604549],
         [13.3517429, 52.5189382]
       ]]
     }
   }

http://geojson.io is a simple tool to preview and edit GeoJSON.

How to convert a shapefile to GeoJSON
`````````````````````````````````````

Most Geographic Information Systems (GIS) such as QGIS or ArcGIS support
the conversion to GeoJSON out of the box. Desktop GIS applications
should automatically reproject the shapefile to WGS84 during the export
to GeoJSON format.

How to optimize GeoJSON for performance
```````````````````````````````````````

The duration of the calculation scales roughly linearly to the number of
vertices in the GeoJSON file. If the calculation takes too long, try to
reduce the number of vertices in the file. This can be achieved in two
ways:

-  Crop the spatial extent of your geographic data to the extent of the
   area where the subjects live (or at least most of them). This makes
   sense if most of your subjects are from the same city or state.
-  Generalize your polygon. This reduces the amount of vertices while
   retaining the general shape of the polygon. This makes sense of the
   resolution of your data is very high. Remember that Castellum derives
   the subjects’ geolocations from their addresses, which refer to
   houses. Therefore, a polygon with a resolution of 10cm has no
   advantage over one with a resolution of 10m, as address data is
   resolved to 10m at best, as determined by typical house sizes.

.. _study-pseudonym-lists:

Manage study pseudonym lists
----------------------------

In the **Pseudonym lists** tab you can create, rename, and delete pseudonym
lists. You can also provide the date at which the pseudonym lists should be
deleted (this is typically defined as part of the study consent).

If there are general lists, you can also define which general pseudonym lists
need to be accessed in the context of this study.

.. note::

    Even if you are not intending to use the pseudonyms provided by Castellum
    (e.g. because the study originated before you started using Castellum) it
    is still a good idea to create a pseudonym list. In that case, the mere
    existence of the list indicates that there is personal data for this study.


.. _study-members:

Manage study members
--------------------

The **Member management** tab allows you to give other staff members (e.g.
recruiters) access to your study. Each row of the table represents a member.
You can change their groups or remove them from your study. The last row allows
you to add new members to the study.

.. note::

    Some features (e.g. recruitment) only become available once the study
    is started. So, some added users may not instantly notice those role
    changes.


.. _study-start:

Start and stop a study
----------------------

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
--------------

1.  :ref:`Find the study <study-search>` at the **Studies** page, click
    **Details** next to the study you wish to finish/resume.

2.  You can find the button **Finish study** next to the study name near to
    other buttons.

3.  Read the text and confirm

.. _study-delete-pseudonym-lists:

Delete pseudonym lists
----------------------

The date when a pseudonym list should be deleted (effectively anonymizing the
research data) is usually defined in the ethics application and the study
consent form.

Once you delete a pseudonym list from Castellum it is no longer possible to
answer export or delete requests. Make sure that all relevant external data has
been deleted before you delete a pseudonym list from Castellum. Then proceed as
follows:

1.  :ref:`Find the study <study-search>` at the **Studies** page, click
    **Details**

2.  Go to the **Pseudonym lists** tab.

3.  Find the relevant pseudonym list and click **Delete**.

4.  Follow the instructions to confirm the deletion.

.. _study-delete:

Delete a study
--------------

When a whole study should be deleted depends on the rules of your specific
organization. We assume that it makes sense to delete all study data after few
years.

1.  :ref:`Find the study <study-search>` at the **Studies** page, click
    **Details**

2.  Make sure the study is finished (see :ref:`study-finish`)

3.  Click on **Delete** under the study name. Confirm the notice **I have made
    sure that all external data related to this study has been destroyed** by
    clicking on **Confirm**


.. _study-search:

Find your study
---------------

Click on **Studies** on the front page

-   In the field **Search** you can look for a certain study
-   By default, only studies in which you are a member are displayed. Click on
    **All studies** to also see studies by other users.
-   You can also filter by **Status**.
