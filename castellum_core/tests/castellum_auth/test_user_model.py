from django.contrib.auth.models import AbstractUser as DjangoUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission


def test_castellum_user_is_django_user(user):
    assert isinstance(user, DjangoUser)


def test_user_get_all_permission_objects(user):
    perm1 = Permission.objects.all()[0]
    user.user_permissions.add(perm1)

    perm2 = Permission.objects.all()[1]
    group = Group.objects.create()
    group.permissions.add(perm2)
    user.groups.add(group)

    assert len(user.get_all_permission_objects()) == 2


def test_user_get_all_permission_objects_unique(user):
    perm1 = Permission.objects.all()[0]
    user.user_permissions.add(perm1)

    group = Group.objects.create()
    group.permissions.add(perm1)
    user.groups.add(group)

    assert len(user.get_all_permission_objects()) == 1
