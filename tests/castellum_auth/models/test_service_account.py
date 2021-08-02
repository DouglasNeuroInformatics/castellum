from django.contrib.auth.models import Permission

from model_bakery import baker

from castellum.castellum_auth.models import User


def test_service_account(study, recruiter):
    serviceaccount = baker.make(User, is_service_account=True, controlled_by=recruiter)
    serviceaccount.user_permissions.add(Permission.objects.get(codename='recruit'))
    assert serviceaccount.has_perm('recruitment.recruit', obj=study)


def test_service_account_not_controlled(study):
    serviceaccount = baker.make(User, is_service_account=True, controlled_by=None)
    serviceaccount.user_permissions.add(Permission.objects.get(codename='recruit'))
    assert not serviceaccount.has_perm('recruitment.recruit', obj=study)


def test_service_account_perm_only_on_service_account(study, conductor):
    serviceaccount = baker.make(User, is_service_account=True, controlled_by=conductor)
    serviceaccount.user_permissions.add(Permission.objects.get(codename='recruit'))
    assert not serviceaccount.has_perm('recruitment.recruit', obj=study)


def test_service_account_perm_only_on_user(study, recruiter):
    serviceaccount = baker.make(User, is_service_account=True, controlled_by=recruiter)
    serviceaccount.user_permissions.add(Permission.objects.get(codename='conduct_study'))
    assert not serviceaccount.has_perm('recruitment.recruit', obj=study)
