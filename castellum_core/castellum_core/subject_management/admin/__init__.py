from django.contrib import admin

from .address import AddressAdmin, CityAdmin, CountryAdmin
from .subject import SubjectAdmin

from ..models import Address, City, Country, Subject


admin.site.register(Address, AddressAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Subject, SubjectAdmin)
