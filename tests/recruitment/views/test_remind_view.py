from django.utils import timezone

from freezegun import freeze_time
from model_bakery import baker

from castellum.recruitment.models import MailBatch
from castellum.recruitment.views import MailRecruitmentRemindView


def test_participations_are_updated_after_reminder(participation, study, client, user):
    now = timezone.now()
    client.force_login(user)
    batch = baker.make(
        MailBatch,
        study=study,
        )
    participation.batch = batch
    participation.save()
    with freeze_time(now):
        remind_view = MailRecruitmentRemindView()
        remind_view.study = study
        remind_view.send_reminder_mail(batch)

    assert participation.updated_at == now
