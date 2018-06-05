from django.db import models
from django.utils.translation import ugettext_lazy as _


class Country(models.Model):
    name = models.CharField(_("name"), max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = "name",
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")


class City(models.Model):
    name = models.CharField(_("name"), max_length=128)
    country = models.ForeignKey(_("Country"), Country, on_delete=models.CASCADE)

    def __str__(self):
        return "{}, {}".format(self.name, self.country.name)

    class Meta:
        ordering = "country__name", "name"
        unique_together = "name", "country"
        verbose_name = _("City")
        verbose_name_plural = _("Cities")


class Address(models.Model):
    city = models.ForeignKey(_("City"), City, on_delete=models.CASCADE)
    zip_code = models.CharField(_("zip code"), max_length=5)
    street = models.CharField(_("street"), max_length=128)
    house_number = models.CharField(_("house_number"), max_length=5)
    additional_information = models.CharField(_("additional information"), max_length=32,
                                              blank=True, default="")

    def __str__(self):
        street = " ".join([self.street, self.house_number, self.additional_information]).strip()
        return "{} {}, {}".format(self.zip_code, self.city.name, street)

    class Meta:
        ordering = ("city__country__name", "city__name", "zip_code", "street", "house_number",
                    "additional_information")
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
