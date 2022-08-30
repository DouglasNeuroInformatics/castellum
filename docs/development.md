# Running a test server

First install some system packages. The exact command depends on your
operating system. This is an example for Ubuntu:

    sudo apt install python3-pip python3-venv npm make gettext sqlite3 libmagic1 gdal-bin libsqlite3-mod-spatialite

After that, running `make` inside the project folder will install all
dependencies and start a test server. You can then log in with username
"admin" and password "password".

**Note**: Python needs to be compiled with
`SQLITE_ENABLE_LOAD_EXTENSION`. This is usually the case for system
packages, but e.g. with pyenv you will have to enable it yourself.

# Things to be aware of when working on the Castellum code

-   We assume a general familiarity with django, especially its
    [class based view system][1].

-   Apps in Castellum are not meant to be reusable or independent. They
    merely act as a way to structure the code.

-   Dependencies between modules follow some rules. Generally speaking,
    there are three layers: A lower layer consisting of models and
    utilities, a middle layer consisting of forms, view mixins, and
    template tags, and an upper layer consisting of views. Modules are
    free to import from lower layers. Importing from the same layers is
    also allowed as long as there are no circular dependencies. For
    example, the recruitment models depend on subject and study models.

-   All models from the contacts app are stored to a separate database.
    This means that there can be no `ForeignKeys` between those models
    and anything else. The `Subject.contact` and `Contact.subject`
    shortcuts provide simple access across databases. See
    `castellum.utils.routers.Router` for details.

-   We use [django's support for object permissions][2] to implement
    study groups. See
    `castellum.studies.backends.StudyPermissionBackend` for details.

-   The available recruitment attributes can be changed at runtime. The
    ones created with `django-admin loaddata attribute_descriptions`
    merely serve as examples. See
    `docs/deployment/dynamic_recruitment_attributes.md` for details.

-   The available groups can be changed at runtime. The ones created
    with `django-admin loaddata groups study_groups` merely serve as
    examples.

-   The Makefile contains many useful shortcuts for development, e.g.
    `make test` or `make lint`.

-   We use [django-stronghold][3] as an additional security layer to
    make sure every view requires authentication. You should not rely on
    that and add the appropriate checks to the view anyway. If you need
    to create a view that should not require authentication, you can use
    the `@public` decorator.

[1]: http://ccbv.co.uk/
[2]: https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#handling-object-permissions
[3]: https://github.com/mgrouchy/django-stronghold
