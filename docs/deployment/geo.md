# Filter by geographic features

Castellum allows to filter by geographical properties of a subject's
address. However, some additional steps are needed. This document
describes how this feature can be activated and used.


## Overview

-   In order to make spatial queries, addresses first need to be
    translated to coordinates (geocoding). This is a slow operation
    which should be done in a cron job.
-   After that we can check wether the subject lives inside of a
    user-defined area.
-   Most dependencies are already installed and configured with
    Castellum by default. However, some additional steps are needed.


## Set up Nominatim

Nominatim is a free geocoder from the OpenStreetMap ecosystem. A public
instance is available at <https://nominatim.openstreetmap.org>. For bulk
geocoding and also for better privacy, it is strongly encouraged to host
a local instance.

Nominatim is already included as a docker service in the example
deployment. However, in order to be usable the software needs to be
initialized with data from OSM. The import is very demanding and can take
hours, depending on the data. This is an example for loading the address
data for Berlin (~20mins):

    cd docs/deployment/example/
    wget 'https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf' -O nominatim/berlin.osm.pbf
    docker-compose run --rm nominatim sh /app/init.sh /data/berlin.osm.pbf postgresdata 4
    rm nominatim/berlin.osm.pbf

Nominatim is also capable of automatically updating the data.
For that you need to adapt `CONST_Replication_Url` in the nominatim
config (`nominatim/local.php` in the example deployment). Then run these
commands:

    docker-compose exec nominatim sudo -u postgres ./src/build/utils/update.php --init-updates
    docker-compose exec nominatim sudo -u postgres ./src/build/utils/update.php --import-osmosis

Further reading:

-   <https://hub.docker.com/r/mediagis/nominatim>
-   <https://nominatim.org/release-docs/latest/admin/Installation/>


## Configure Castellum

-   Add `'django.contrib.gis'` and `'castellum.geofilters'` to
    `INSTALLED_APPS`
-   Configure `NOMINATIM`. You only have to set `domain` to point geopy
    to the domain of your local Nominatim instance. The port only needs
    to be set if it's a non-standard one. The [geopy documentation]
    (https://geopy.readthedocs.io/en/stable/#geopy.geocoders.Nominatim)
    also lists available options.
-   setup a cron job for geocoding. Running it once a week is
    recommended. The management command to use is called `geocode_all`.
    Note that invalid addresses will be sent to the geocoder every time
    the script is run. Therefore the time required to run the geocoding
    script depends on the number of invalid addresses as well as the
    number of not yet geocoded addresses.  Running the script repeatedly
    only speeds up the second part, not the first.  Castellum has no way
    to determine if an address doesn't exist at all, is misspelled or
    can't be geocoded because it's not in the database used for
    geocoding.
