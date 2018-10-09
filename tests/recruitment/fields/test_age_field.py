import pytest


@pytest.mark.parametrize('age,expected', (
    (2, True),
    (-2, False),
))
def test_error_if_age_out_of_limits(client, user, filter_group, age, expected):
    client.force_login(user)
    url = '/recruitment/filter/{}/{}/'.format(filter_group.study.pk, filter_group.pk)
    response = client.post(url,  {
        "form-0-field_name": "date_of_birth",
        "form-0-group": filter_group.pk,
        "form-0-id": 1,
        "form-0-operator": "gt",
        "form-0-value_0": age,
        "form-0-value_1": "years",
        "form-INITIAL_FORMS": 1,
        "form-MAX_NUM_FORMS": 1000,
        "form-MIN_NUM_FORMS": 0,
        "form-TOTAL_FORMS": 1,
    })

    if expected:
        assert b"is-invalid" not in response.content
    else:
        assert b"is-invalid" in response.content
