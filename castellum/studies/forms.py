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

from django import forms

from castellum.castellum_auth.models import User
from castellum.utils.forms import ReadonlyModelForm

from . import models


class StudyForm(ReadonlyModelForm):
    class Meta:
        model = models.Study
        fields = [
            'name',
            'contact_person',
            'principal_investigator',
            'affiliated_scientists',
            'affiliated_research_assistants',
            'description',
            'keywords',
            'study_type',
            'data_sensitivity',
            'consent',
            'min_subjects_count',
            'expense_allowance',
            'sessions_start',
            'sessions_end',
        ]
class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all())


class MemberForm(forms.ModelForm):
    class Meta:
        model = models.StudyMembership
        fields = ('groups',)
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }
