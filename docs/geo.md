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
    castellum by default. However, some additional steps are needed.


## Example use case

If the desired participants for a study should be older than 40 years
and live in an area where the noise from an airport is over 40dB you
would create and upload a GeoJSON file with a (multi)polygon spanning
the area where this condition applies. Afterwards proceed as usual with
setting the filter for age in the study filter UI.  The resulting
subjects in the recruitment interface match the filter condition AND
their contact address is located inside the uploaded polygon.

## Geocoding

### Nominatim

Nominatim is a free geocoder from the OpenStreetMap ecosystem. A public
instance is available at <https://nominatim.openstreetmap.org>. For bulk
geocoding and also for better privacy, it is strongly encouraged to host
a local instance.

Nominatim is already included as a docker service in the example
deployment. However, in order to be usable the software needs to be
initialized with data from OSM. The import is very demanding and can take
hours, depending on the data. This is an example for loading the address
data for Berlin (~20mins):

    cd docs/example_deployment/
    wget 'https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf' -O nominatim/berlin.osm.pbf
    docker-compose run --rm nominatim sh /app/init.sh /data/berlin.osm.pbf postgresdata 4
    rm nominatim/berlin.osm.pbf

If everything worked out you can query nominatim like this:

    curl 'http://localhost:7070/search?city=berlin&country=germany&street=Lentzeallee%2094&limit=1&format=json'

Nominatim is also capable of automatically updating the data.
For that you need to adapt `CONST_Replication_Url` in the nominatim
config (`nominatim/local.php` in the example deployment). Then run these
commands:

    docker exec -it exampledeployment_nominatim_1 sudo -u postgres ./src/build/utils/update.php --init-updates
    docker exec -it exampledeployment_nominatim_1 sudo -u postgres ./src/build/utils/update.php --import-osmosis-all

Further reading:

-   <https://hub.docker.com/r/mediagis/nominatim>
-   <https://nominatim.org/release-docs/latest/admin/Installation/>

### Configure Castellum

-   Add `'castellum.geofilters'` to `INSTALLED_APPS`
-   Configure `NOMINATIM`. You only have to set `domain` to point geopy
    to the domain of your local Nominatim instance. The port only needs
    to be set if it's a non-standard one. The [geopy documentation]
    (https://geopy.readthedocs.io/en/stable/#geopy.geocoders.Nominatim)
    also lists available options.
-   setup a cron job for geocoding. Running it once a week is
    recommended. The management command to use is called `geocode`.
    Note that invalid addresses will be sent to the geocoder every time
    the script is run. Therefore the time required to run the geocoding
    script depends on the number of invalid addresses as well as the
    number of not yet geocoded addresses.  Running the script repeatedly
    only speeds up the second part, not the first.  Castellum has no way
    to determine if an address doesn't exist at all, is misspelled or
    can't be geocoded because it's not in the database used for
    geocoding.


## Create a geo filter

### GeoJSON format

Provide a valid [GeoJSON](https://tools.ietf.org/html/rfc7946) file with
exactly one feature of type "Polygon" or "MultiPolygon". Castellum will
then filter all subjects that live inside this (multi)polygon, so it
should enclose all areas where the conditions for recruitment are met.
Note that the Coordinate Reference System (CRS) must be WGS84
(EPSG:4326).

This is an example of a valid GeoJSON file:

```
{
  "type": "Feature",
  "properties": {},
  "geometry": {
    "type": "Polygon",
    "coordinates": [[
      [13.3517429, 52.5189382],
      [13.2908489, 52.5165476],
      [13.3463410, 52.4848593],
      [13.3512518, 52.4468630],
      [13.3964313, 52.4785787],
      [13.4627272, 52.4504546],
      [13.4308069, 52.4893448],
      [13.4730399, 52.5192370],
      [13.4141102, 52.5180417],
      [13.3821899, 52.5604549],
      [13.3517429, 52.5189382]
    ]]
  }
}
```

<http://geojson.io> is a simple tool to preview and edit GeoJSON.

### How to convert a shapefile to GeoJSON

Most Geographic Information Systems (GIS) such as QGIS or ArcGIS support
the conversion to GeoJSON out of the box. Before exporting the GeoJSON
file merge all polygons and multipolygons in the layer into one feature,
as the geofilter will fail if there is more than one feature in the
file. Desktop GIS applications should automatically reproject the
shapefile to WGS84 during the export to GeoJSON format.

### How to optimize GeoJSON for performance

The duration of the calculation scales roughly linearly to the number of
vertices in the GeoJSON file. If the calculation takes too long, try to
reduce the number of vertices in the file. This can be achieved in two
ways:

-   Crop the spatial extent of your geographic data to the extent of the
    area where the subjects live (or at least most of them). This makes
    sense if most of your subjects are from the same city or state.
-   Generalize your polygon. This reduces the amount of vertices while
    retaining the general shape of the polygon. This makes sense of the
    resolution of your data is very high. Remember that Castellum
    derives the subjects' geolocations from their addresses, which refer
    to houses. Therefore, a polygon with a resolution of 10cm has no
    advantage over one with a resolution of 10m, as address data is
    resolved to 10m at best, as determined by typical house sizes.
