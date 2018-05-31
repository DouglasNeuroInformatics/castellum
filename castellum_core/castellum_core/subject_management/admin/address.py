from django.contrib import admin


class CountryAdmin(admin.ModelAdmin):
    pass


class CityAdmin(admin.ModelAdmin):
    list_display = "name", "country",
    list_per_page = 200


class AddressAdmin(admin.ModelAdmin):
    list_display = "city", "zip_code", "street", "house_number", "additional_information"
    list_per_page = 200
