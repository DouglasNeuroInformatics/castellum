FAQs
====

How can I contact subjects by pseudonym after the study is finished?
--------------------------------------------------------------------

Finding subjects by pseudonym is no longer possible once the study has
finished. If you need to contact a subject after the study is finished we
recommend to :ref:`resume the study <study-finish>` temporarily.


How can I edit subject data as recruiter or study conductor?
------------------------------------------------------------

Recruiters and conductors are only allowed to access subject data of
participants within study context. Yet, this workflow allows to edit the subject
data of them:

- Search for the participant via **Subjects** on the home screen.
- Select either **Recruitment** or **Execution** (whichever is applicable) in
  the **Matches** list to go to the subject details view.
- Click on **Update data** and select appropriate categories that need to be
  edited. Edit and save the forms accordingly.

Although it has a slightly different look and feel you can get reference on
editing subject data here: :ref:`subject-edit`.


What should I do if a subject doesn't show up for their appointment?
--------------------------------------------------------------------

Castellum allows you to mark a subject as :ref:`unreliable
<execution-annotations>`. In our experience, many unreliable subjects are not
aware how expensives no-shows can be. Contacting them and explaining the
situation can help avoiding no-shows in the future.


How can I use pseudonyms with LimeSurvey?
-----------------------------------------

1. In LimeSurvey, add a new question called "pseudonym" and hide it (Display -
   Always hide this question)
2. In Castellum, :ref:`add a new Pseudonym List <study-pseudonym-lists>` called
   "LimeSurvey".
3. Send a personalized LimeSurvey link to each participant. For example: If the
   participant's pseudonym is "abc" and the basic LimeSurvey link is
   ``https://example.limesurvey.net/123456?lang=de``, the personalized link is
   ``https://example.limesurvey.net/123456?lang=de&pseudonym=abc``.
4. After the participants have answered the questionnaire, go to LimeSurvey and
   click on **Responses** to download the data. The pseudonyms will be included
   as the output of the hidden field "pseudonym".
5. In Castellum, :ref:`find the subject for each pseudonym
   <subject-by-pseudonym>` to link the questionnaire results to your other
   data.

.. NOTE::
   It is important to use a separate pseudonym list because the pseudonyms
   are sent out along with the name and email address. Anyone who has access to
   that email (e.g. many people working at the company that provides the email
   account) will be able to match this pseudonym to the real person.


Why are recruiters not allowed to add new subjects to the database?
-------------------------------------------------------------------

I order to avoid duplicate entries, users have to search for existing matches
before they are allowed to :ref:`enter a new subject <subject-create>` into the
database. In other words: In order to be allowed to enter a new subject, users
must have the permission to see all existing subjects.

That is why users who are only allowed to see the subjects in their own study
(such as recruiters) cannot add new subjects. They have to get support from
other users who have these extended permissions.
