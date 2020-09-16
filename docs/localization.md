# Localization

Castellum by default provides an english and german localization. This
document gives an overview of the related features and explains how
to change the set of available languages.

## User interface

-   User interface strings in the code are always written in english. A
    german translation is included.
-   Some models that are created via the admin interface (i.e.
    `StudyType` and `AttributeDescription`) are treated as part of the
    UI and can therefore be translated.
-   Users can select a language using the language switcher that is
    always available in the header.
-   The available languages are defined in `settings.PARLER_LANGUAGES`.
-   The default language is defined in `settings.LANGUAGE_CODE`

### Changing the set of available languages

You are free to change `settings.PARLER_LANGUAGES` and
`settings.LANGUAGE_CODE`. However, there are some caveats:

-   Apart from the english default, only a german translation is
    included. If you want to add another language you should create the
    relevant translation file yourself. See
    <https://docs.djangoproject.com/en/stable/ref/django-admin/#makemessages>.
-   If you change `settinge.PARLER_LANGUAGES` django will warn you that
    some model changes are not reflected in the migrations. It is
    usually safe to ignore that warning because this specific migration
    would not actually change the database. Of course you can also
    generate the migration.
-   The included fixtures and demo contents were created with english
    and german in mind and might lead to unexpected results with other
    languages.

## Emails

Mails are defined either in settings or in the UI, so the language
depends on what is entered there. However, some messages may contain
automatic formatting e.g. for dates, so the locale is still important.

There are two different contexts for sending mails: "internal" mails
directed at users and "recruitment" mails directed at subjects. The
primary locale for these contexts can be defined as part of
`settings.CASTELLUM_MAIL`.

Some mails allow to provide a secondary "fallback" body in a different
language (often english). This secondary language is defined in
`settings.CASTELLUM_FALLBACK_LANGUAGE`. The markers used to separate
both versions are defined in
`settings.CASTELLUM_FALLBACK_LANGUAGE_MARKERS`.

## Other content

Castellum does not provide special features to translate content (e.g.
study descriptions). You can of course enter several language version
into a single text field.

## Example: Italian

Castellum does not provide an Italian translation. Assuming everyone
involved knows english but hardly anyone knows german the simplest
option is to remove german from the set of available languages:

    LANGUAGE_CODE = 'en'
    PARLER_LANGUAGES = {
        None: [
            {'code': 'en'},
        ],
    }

However, you can provide Italian texts for all recruitment mails and
configure castellum to use the corresponding locale:

    CASTELLUM_FALLBACK_LANGUAGE = 'en'
    CASTELLUM_MAIL = {
        'recruitment': {
            'language': 'it',
        },
        'internal': {
            'subject_prefix': '[Castellum] ',
        },
    }
