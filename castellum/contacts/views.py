# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import ListView

from .models import Street


class StreetView(LoginRequiredMixin, ListView):
    model = Street
    ordering = 'name'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(name__istartswith=self.request.GET['q'])
        return qs[:10]

    def get(self, request, *args, **kwargs):
        data = [street.name for street in self.get_queryset()]
        return JsonResponse({'streets': data})
