# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils.translation import gettext_lazy as _

from castellum.contacts.models import Contact
from castellum.recruitment import filter_queries
from castellum.recruitment.models import Attribute
from castellum.recruitment.models import Participation

from .models import Subject


def get_attribute_filter(pk, operator, value, **kwargs):
    attr = Attribute.objects.get(pk=pk)
    return (
        attr.field.get_filter_display(operator, value),
        Subject.objects.filter(
            attr.field.filter_to_q(operator, value, **kwargs)
            & filter_queries.has_privacy_level(attr.privacy_level)
            & filter_queries.has_consent()
        ).count(),
    )


def get_contact_updated():
    return _('Contact data updated in last 6 months'), Contact.objects.filter(
        updated_at__gte=datetime.date.today() - relativedelta(months=6),
    ).count()


def get_attributes_complete():
    completeness, total = filter_queries.completeness_expr()
    return _('Complete recruitment attributes'), (
        Subject.objects
        .alias(completeness=completeness)
        .filter(completeness=total, deceased=False, blocked=False)
        .count()
    )


def get_participated_in_study():
    return _('Took part in a study'), Subject.objects.filter(
        participation__status__in=Participation.INVITED_SET,
    ).distinct().count()


def get_recruitable():
    return _('Currently recruitable'), Subject.objects.filter(
        filter_queries.has_consent() & ~models.Q(
            pk__in=Participation.objects.filter(
                filter_queries._reverse_exclusive_studies()
            ).values('subject')
        ),
    ).count()
