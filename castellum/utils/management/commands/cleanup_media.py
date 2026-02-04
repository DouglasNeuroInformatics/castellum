# SPDX-FileCopyrightText: 2018-2026 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Since Django 1.3, media files are no longer deleted with the
corresponding model.

https://docs.djangoproject.com/en/stable/releases/1.3/#deleting-a-model-doesn-t-delete-associated-files
"""

import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import FileField


def iter_models():
    for app_config in apps.get_app_configs():
        yield from app_config.get_models()


def iter_file_fields(model):
    for field in model._meta.get_fields():
        if isinstance(field, FileField):
            yield field


def iter_media_files():
    for root, _dirs, files in os.walk(settings.MEDIA_ROOT):
        for filename in files:
            yield Path(root) / filename


def get_used_files():
    files = []
    for model in iter_models():
        for field in iter_file_fields(model):
            files += model.objects.values_list(field.name, flat=True)
    return [settings.MEDIA_ROOT / f for f in files if f]


class Command(BaseCommand):
    help = 'Remove unused uploaded files.'

    def handle(self, *args, **options):
        used_files = get_used_files()
        for path in iter_media_files():
            if path not in used_files:
                if options['verbosity'] > 0:
                    self.stdout.write(f'Deleting unused media file {path}')
                path.unlink()
