# Dynamic recruitment attributes

Castellum does not dictate a fixed set of recruitment attributes that
can be stored. Instead, it allows to define your own attributes.

However, that flexibility comes with a cost: There are certain limits to
what you can define and migrating existing data is not that simple.

## Technical Overview

Attributes are stored in the database as JSON. This allows to store a
wide range of values and even allows basic queries.

The schema is also defined in the database. Every attribute is defined
in an `Attribute` which contains the information necessary to
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

## Creating Attributes

You can create attributes in the django admin UI at
`/admin/recruitment/attribute/add/`.

The management command `loaddata attributes` will create a small set of
example attributes. If you don't want to create your schema from scratch
you can use them as a starting point.

## Changing Attributes

While changing informational data such as label and help text is safe,
changing behavior (field type and choices) usually requires custom data
migrations. There is currently no special support for attribute
migrations in Castellum. However, it should be possible to create such a
migration using the available django interfaces.

As a general rule, we recommend creating a new `Attribute` and
deprecating the old one over modifying an existing one.

## Deleting Attributes

If you delete an attribute, all related data will automatically be
deleted along with it. Note that subject filters for this attribute will
also be deleted.
