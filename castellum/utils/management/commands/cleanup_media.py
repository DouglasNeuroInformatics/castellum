# (c) 2018-2020
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

"""
Since Django 1.3, media files are no longer deleted with the
corresponding model.

https://docs.djangoproject.com/en/stable/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files
"""


import os

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import FileField


def iter_models():
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            yield model


def iter_file_fields(model):
    for field in model._meta.get_fields():
        if isinstance(field, FileField):
            yield field


def iter_media_files():
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            yield os.path.join(root, filename)


def get_used_files():
    files = []
    for model in iter_models():
        for field in iter_file_fields(model):
            files += model.objects.values_list(field.name, flat=True)
    return [os.path.join(settings.MEDIA_ROOT, f) for f in files if f]


class Command(BaseCommand):
    help = 'Remove unused uploaded files.'

    def handle(self, *args, **options):
        used_files = get_used_files()
        for path in iter_media_files():
            if path not in used_files:
                if options['verbosity'] > 0:
                    self.stdout.write('Deleting', path)
                os.unlink(path)
