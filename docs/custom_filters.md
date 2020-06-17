# Custom filters

In castellum, there are two different ways to create filters for your
study: The simple mode allows you to create several conditions that must
all match. The advanced mode allows you to find subjects that match at
least one of several of such groups of conditions.

But there is a third option that is even more powerful than the advanced
mode: Custom filters. They are meant as a loophole to provide maximum
flexibility, but that comes at the cost of simplicity.

To use a custom filter, you must go through these steps:

## Create a django app

The simplest option is to create a folder in `castellum/` on the server.
For a cleaner approach, you might want to read about [reusable app][1]
in the django documentation.

You also need to register your app by adding it to `INSTALLED_APPS` in
the settings:

    INSTALLED_APPS += ['path.to.my_app']

## Create the filter

Inside the app, create a file called `custom_filters.py` that looks
something like this:

    from django.db.models import Q
    from castellum.recruitment import filter_registry

    @filter_registry.register('myfilter')
    def myfilter(**kwargs):
        return Q(data__d1='test')


The filter needs to be registered with a name and must return a [Q
object][2]. The possible conditions and arguments depend on internals
that are not guaranteed to be stable.

## Assign a custom filter to a study

After restarting castellum, you can assign a custom filter to a study
from the admin interface. If a custom filter is assigned, the regular
filter interface is blocked.

## Security considerations

Custom filters are executed in the context of castellum and have read
and write access to all data. They should therefore be carefully
reviewed before installation.

[1]: https://docs.djangoproject.com/en/stable/intro/reusable-apps/
[2]: https://docs.djangoproject.com/en/stable/ref/models/querysets/#django.db.models.Q
