# Filter by geographic features

Castellum allows to filter by geographical properties of a subject's
address. However, some additional steps are needed. This document
describes how this feature can be activated and used.


## Overview

-   In order to make geographical calculations, addresses first need
    to be translated to coordinates (geocoding). This is a slow
    operation which should be done in a cron job.
-   After that we can check wether the subject lives inside of a
    user-defined area.
-   Most dependencies are already installed and configured with
    castellum by default. However, some additional steps are needed.

## Geocoding

### Nominatim

Nominatim is a free geocoder from the OpenStreetMap ecosystem. A public
instance is available at <https://nominatim.openstreetmap.org>. For bulk
geocoding and also for better privacy, it is strongly encouraged to host
a local instance.

Nominatim is already included as a docker service in the example
deployment. However, the software itself is not very useful without any
data. The import is very demanding and can take hours, depending on the
data. This is an example for loading the address data for Berlin
(~20mins):

    mkdir nominatim
    wget 'https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf' -O nominatim/berlin.osm.pbf
    docker-compose run --rm nominatim sh /app/init.sh /data/berlin.osm.pbf postgresdata 4
    rm nominatim/berlin.osm.pbf

If everything worked out you can query nominatim like this:

    curl 'http://localhost:7070/search?city=berlin&country=germany&street=Lentzeallee%2094&limit=1&format=json'

Further reading:

-   <https://hub.docker.com/r/mediagis/nominatim>
-   <https://nominatim.org/release-docs/latest/admin/Installation/>

### Configure Castellum

-   Add `'castellum.geofilters'` to `INSTALLED_APPS`
-   Configure `NOMINATIM`. The [geopy documentation](https://geopy.readthedocs.io/en/stable/#geopy.geocoders.Nominatim)
    lists available options.
-   setup a cron job for geocoding


## Create a geo filter

### GeoJSON format
### How to convert a shapefile to GeoJSON
### How to optimize GeoJSON for performance
