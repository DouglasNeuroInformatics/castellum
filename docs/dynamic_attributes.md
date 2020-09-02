# Dynamic Attributes

Castellum does not dictate a fixed set of attributes that can be stored.
Instead, it allows to define your own attributes.

However, that flexibility comes with a cost: There are certain limits to
what you can define and migrating existing data is not that simple.

## Technical Overview

Attributes are stored in the database as JSON. This allows to store a
wide range of values and even allows basic queries.

The schema is also defined in the database. Every attribute is defined
in an `AttributeDescription` which contains the information necessary to
create a [`FormField`](https://docs.djangoproject.com/en/stable/ref/forms/fields/#core-field-arguments).
This includes informational data such as label and help text as well as
the field type which defines behavior.

## Available Field Types

--------------------- ----------------- ------------ ----------
field type            attribute value   filter value comparison
--------------------- ----------------- ------------ ----------
`BooleanField`        boolean           boolean      nominal
`IntegerField`        integer           integer      ordinal
`CharField`           string            string       nominal
`ChoiceField`         choice            choice       nominal
`MultipleChoiceField` choice (multiple) choice       nominal
`OrderedChoiceField`  choice            choice       ordinal
`DateField`           date              date         ordinal
`AgeField`            date              age          ordinal
--------------------- ----------------- ------------ ----------

## Creating Attribute Descriptions

You can create attribute descriptions in the django admin UI at
`/admin/recruitment/attributedescription/add/`.

This GUI also allows to export and import attribute descriptions as
JSON. This allows organizations to easily exchange attribute
descriptions.

The management command `create_attribute_descriptions` will create a
small set of example attribute descriptions. If you don't want to create
your schema from scratch you can use them as a starting point.

## Changing Attribute Descriptions

While changing informational data such as label and help text is safe,
changing behavior (field type and choices) usually requires custom data
migrations. There is currently no special support for attribute
migrations in castellum. However, it should be possible to create such a
migration using the available django interfaces.

As a general rule, we recommend creating a new `AttributeDescription`
and deprecating the old one over modifying an existing one.
