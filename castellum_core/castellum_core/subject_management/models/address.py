from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = "name",
        verbose_name = "Country"
        verbose_name_plural = "Countries"


class City(models.Model):
    name = models.CharField(max_length=128)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return "{}, {}".format(self.name, self.country.name)

    class Meta:
        ordering = "country__name", "name"
        unique_together = "name", "country"
        verbose_name = "City"
        verbose_name_plural = "Cities"


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=5)
    street = models.CharField(max_length=128)
    house_number = models.CharField(max_length=5)
    additional_information = models.CharField(max_length=32, blank=True, default="")

    def __str__(self):
        street = " ".join([self.street, self.house_number, self.additional_information]).strip()
        return "{} {}, {}".format(self.zip_code, self.city.name, street)

    class Meta:
        ordering = ("city__country__name", "city__name", "zip_code", "street", "house_number",
                    "additional_information")
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
