.. _study-execution:

===============
Study execution
===============

Study execution provides you with a set of features needed to conduct a study.
For a start, it lists all participating subjects of a study. Most importantly it
allows you to obtain pseudonyms for each participant as described here:
:ref:`subject-get-pseudonym`.

The **List** tab simply shows all participants regardless of whether they have
an appointment. For each entry it will present a color coded reliability score,
the appointment states and assigned tags. The **Calendar** tab allows you to
view all participants with appointments (week, month and list views). The
**By pseudonym** tab offers to find a participant by specifying study
specific pseudonyms (see :ref:`subject-by-pseudonym`).

The **News** tab offers a mail form to contact all interested participants on
recent study outcomes, study specific events or similar. After sending such a
message and if applicable Castellum will send you an additional mail that
lists all participants who want to be informed via postal mail.

The **Tags** tab allows you to edit, add or delete tags that should be used to
tag participants during study execution in order to support your workflows or
the like.

The **Progress** tab gives insights on the current number of participants and
appointments.


.. _execution-attribute-export:

Export attributes of participants
=================================

You may want to initially populate your scientific data with a listing of
known attributes of the participants. Therefore, Castellum allows you to export
attributes of all participants sorted by a pseudonym.

.. note::

   This feature only allows to export those attributes that are specified in
   study management as **Exportable recruitment attributes**.

   You are only allowed to export attributes if your privacy level is matching
   those of the *highest rated* attribute and/or participant.

   If there is more than one study specific pseudonym domain set up in study
   management you will have to select the domain that should be used for export.

The export will provide a zipped file containing of an attributes file and a
schema file that allows you to comprehend the actual values in the attributes
file. Depending on your Castellum setup the attributes file will be provided as
custom ``json`` or ``tsv`` (as `BIDS compliant participants file
<https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html#participants-file>`_)
file.


.. _execution-annotations:

Conductor Annotations on participants
=====================================

The participant details in study execution allow you to add additional hints
that may be important for you or other conductors when working with this
participant. The **Hints** tab offers you

-  to specify the interest in future study outcomes. All interested participants
   can be contacted later via the **News** tab in study execution.
-  to assign a conductor who should be working with the participant.

   .. warning::

      In case you have study members who are recruiter and conductor: Please note
      that assignments are context aware. In other words assigned recruiters will
      not be automatically marked as assigned conductors in the study execution
      and vice versa.

-  select **Execution tags** that may help to comply with processes or similar.
   If the standard tags are not sufficient for your workflow click on
   **Manage tags** to add, edit or delete them.
-  mark the participant as unreliable. This information will be used for future
   study recruitments or study executions allowing other Castellum users to
   assess a potential subject and take precautions if necessary.
