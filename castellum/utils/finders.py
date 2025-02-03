import os

from django.conf import settings
from django.contrib.staticfiles import utils as django_utils
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage

"""
If we would just add node_modules to STATICFILES_DIRS,
collectstatic would copy a lot of files that we don't
actually need.

See also https://github.com/deeprave/django-npm-finder
"""


def flatten_patterns(patterns):
    if patterns is None:
        return ['*']
    return [
        os.path.join(module, module_pattern)
        for module, module_patterns in patterns.items()
        for module_pattern in module_patterns
    ]


class NpmFinder(BaseFinder):
    def __init__(self, apps=None, *args, **kwargs):
        self.storage = FileSystemStorage(location=os.path.join(
            getattr(settings, 'NPM_ROOT_PATH', '.'),
            'node_modules',
        ))
        self.match_patterns = flatten_patterns(
            getattr(settings, 'NPM_FILE_PATTERNS', None)
        )

    def find(self, path, all=False):
        if not django_utils.matches_patterns(path, self.match_patterns):
            return []
        elif not self.storage.exists(path):
            return []
        elif all:
            return [self.storage.path(path)]
        else:
            return self.storage.path(path)

    def list(self, ignore_patterns):
        return [
            (p, self.storage)
            for p in django_utils.get_files(self.storage, ignore_patterns)
            if django_utils.matches_patterns(p, self.match_patterns)
        ]
