from castellum.utils.management.commands import cleanup_media


def test_iter_file_fields():
    fields = []
    for model in cleanup_media.iter_models():
        for field in cleanup_media.iter_file_fields(model):
            fields.append('{}.{}'.format(model._meta.label, field.name))
    assert fields == [
        'studies.Study.geo_filter',
        'studies.Study.consent',
        'subjects.ConsentDocument.file',
        'subjects.Consent.file',
        'recruitment.Participation.consent',
    ]
