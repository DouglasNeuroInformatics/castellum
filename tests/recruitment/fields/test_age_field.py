import pytest


@pytest.mark.parametrize('age,expected', (
    (-1, False),
    (0, True),
    (1, True),
    (999, True),
    (1000, True),
    (1001, False),
))
def test_error_if_age_out_of_limits(
    client, attribute_descriptions, member, subject_filter_group, age, expected
):
    client.force_login(member)
    url = '/studies/{}/recruitmentsettings/filters/{}/'.format(
        subject_filter_group.study.pk, subject_filter_group.pk
    )
    response = client.post(url, {
        "form-0-description": 3,
        "form-0-group": subject_filter_group.pk,
        "form-0-operator": "gt",
        "form-0-value_0": age,
        "form-0-value_1": "years",
        "form-INITIAL_FORMS": 0,
        "form-MAX_NUM_FORMS": 1000,
        "form-MIN_NUM_FORMS": 0,
        "form-TOTAL_FORMS": 1,
    })

    if expected:
        assert b"is-invalid" not in response.content
    else:
        assert b"is-invalid" in response.content
