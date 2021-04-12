# (c) 2018-2021
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

from django import forms
from django.contrib import admin

from parler.admin import TranslatableAdmin

from castellum.recruitment.filter_registry import custom_filters

from . import models


def custom_filter_choices():
    return [(None, '---')] + [(k, k) for k in sorted(custom_filters.keys())]


class StudyForm(forms.ModelForm):
    custom_filter = forms.ChoiceField(choices=custom_filter_choices, required=False)

    class Meta:
        model = models.Study
        fields = '__all__'


class StudySessionInline(admin.TabularInline):
    model = models.StudySession


class StudyAdmin(admin.ModelAdmin):
    form = StudyForm
    inlines = [StudySessionInline]
    search_fields = ['name']


admin.site.register(models.Resource)
admin.site.register(models.Study, StudyAdmin)
admin.site.register(models.StudyGroup)
admin.site.register(models.StudyMembership)
admin.site.register(models.StudyType, TranslatableAdmin)
admin.site.register(models.StudyTypeEventFeed)
