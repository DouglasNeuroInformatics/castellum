from django.contrib.staticfiles.storage import (
    ManifestStaticFilesStorage as BaseManifestStaticFilesStorage,
)


class ManifestStaticFilesStorage(BaseManifestStaticFilesStorage):
    support_js_module_import_aggregation = True
