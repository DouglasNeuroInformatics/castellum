# SPDX-FileCopyrightText: 2018-2025 MPIB <https://www.mpib-berlin.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPI-CBS <https://www.cbs.mpg.de/>
# SPDX-FileCopyrightText: 2018-2019 MPIP <http://www.psych.mpg.de/>
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class NpmFinder(BaseFinder):
    """
    If we would just add node_modules to STATICFILES_DIRS,
    collectstatic would copy a lot of files that we don't
    actually need.

    See also https://github.com/deeprave/django-npm-finder
    """

    def __init__(self, apps=None, *args, **kwargs):
        self.storage = FileSystemStorage(location=settings.NPM_PATH)

    def find(self, path, all=False):
        full_path = self.storage.path(path)
        return [full_path] if all else full_path

    def list(self, ignore_patterns):
        return [(str(p), self.storage) for p in settings.NPM_FILES]
