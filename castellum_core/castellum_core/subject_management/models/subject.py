# (c) 2018
#     MPIB <https://www.mpib-berlin.mpg.de/>,
#     MPI-CBS <https://www.cbs.mpg.de/>,
#     MPIP <http://www.psych.mpg.de/>
#
# This file is part of Castellum.
#
# Castellum is free software; you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Castellum is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Castellum. If not, see
# <http://www.gnu.org/licenses/>.

import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from . import Address


class Subject(models.Model):
    GENDER = (
        ("f", _("female")),
        ("m", _("male")),
        ("*", _("diverse")),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    first_name = models.CharField(_("first name"), max_length=64)
    last_name = models.CharField(_("last name"), max_length=64)
    title = models.CharField(_("title"), max_length=64, blank=True)

    gender = models.CharField(_("gender"), max_length=1, choices=GENDER, default="f")

    birthday = models.DateField(_("birthday"))

    address = models.ForeignKey(Address, blank=True, null=True, verbose_name=_("Address"),
                                on_delete=models.SET_NULL)
    email = models.EmailField(_("email"), max_length=128, blank=True)
    phone_number = models.CharField(_("phone number"), max_length=32, blank=True)
    phone_number_alternative = models.CharField(_("phone number alternative"), max_length=32,
                                                blank=True)

    def get_absolute_url(self):
        return reverse('subject_management:subject_detail', args=[self.pk])

    def full_name(self):
        name = self.first_name + ' ' + self.last_name
        if self.title:
            name = self.title + ' ' + name
        return name
