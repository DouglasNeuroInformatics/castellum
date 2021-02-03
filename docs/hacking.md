## Development setup

The following commands will install everything and start a local testserver (on ubuntu):

    sudo apt install python3-pip python3-venv npm make docker-compose gettext gdal-bin python3-psycopg2
    cd castellum
    make install_githooks
    make  # start castellum

You can login with user "admin" and password "password".

# Things to be aware of when working on the castellum code

-   We assume a general familiarity with django, especially its
    [class based view system][1].

-   Apps in castellum are not meant to be reusable or independent. They
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
    ones created with `django-admin create_attribute_descriptions`
    merely serve as examples. See `dynamic_attributes.md` for details.

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
