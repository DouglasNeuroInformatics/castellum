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

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Country(models.Model):
    name = models.CharField(_('Name'), max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = 'name',
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')


class City(models.Model):
    name = models.CharField(_('Name'), max_length=128)
    country = models.ForeignKey(Country, verbose_name=_('Country'), on_delete=models.CASCADE)

    def __str__(self):
        return "{}, {}".format(self.name, self.country.name)

    class Meta:
        ordering = 'country__name', 'name'
        unique_together = 'name', 'country'
        verbose_name = _('City')
        verbose_name_plural = _('Cities')


class AddressManager(models.Manager):
    def get_queryset(self):  # pragma: no cover
        return super().get_queryset().select_related('city')


class Address(models.Model):
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.CASCADE)
    zip_code = models.CharField(_('Zip code'), max_length=5)
    street = models.CharField(_('Street'), max_length=128)
    house_number = models.CharField(_('House number'), max_length=5)
    additional_information = models.CharField(_('Additional information'), max_length=32,
                                              blank=True)

    objects = AddressManager()

    def __str__(self):
        street = " ".join([self.street, self.house_number, self.additional_information]).strip()
        return "{}, {} {}".format(street, self.zip_code, self.city.name)

    class Meta:
        ordering = ('city__country__name', 'city__name', 'zip_code', 'street', 'house_number',
                    'additional_information')
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
