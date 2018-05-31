from django.contrib import admin


class SubjectAdmin(admin.ModelAdmin):
    list_display = "first_name", "last_name", "address", "email", "phone_number"
    list_display_links = "first_name", "last_name"
    list_per_page = 200
    search_fields = "first_name", "last_name"

    fieldsets = (
        (None, {
            "fields": (
                ("first_name", "last_name"),
                "gender",
                "birthday",
            ),
        }),
        ("Contact Data", {
            "fields": ("address", "email", ("phone_number", "phone_number_alternative"))
        }),
    )
