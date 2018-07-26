from castellum.castellum_auth.forms import UserCreationAdminForm
from castellum.castellum_auth.models import User


def test_with_password(db):
    form = UserCreationAdminForm({
        'username': 'test',
        'password1': 'Eoc5wei8',
        'password2': 'Eoc5wei8',
    })
    assert form.is_valid()
    form.save()
    assert User.objects.get().has_usable_password() is True


def test_without_password(db):
    form = UserCreationAdminForm({
        'username': 'test',
    })
    assert form.is_valid()
    form.save()
    assert User.objects.get().has_usable_password() is False
