# Autocompletion for street names

To avoid typos, castellum provides auto completion for some fields such
as country, city, and street. The completion for country and city is
based on existing values from the database. This would not be a sensible
approach for street names though. Instead, it is possible to provide a
list of available street names.

A simple way to do that is to import street names from OpenStreetMap.
This is an example for  Berlin:

    wget 'https://download.geofabrik.de/europe/germany/berlin-latest.osm.bz2'
    bzip2 -d berlin-latest.osm.bz2
    django-admin import_osm_street_names --clear berlin-latest.osm
    rm berlin-latest.osm
