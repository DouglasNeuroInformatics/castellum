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

Provide a valid GeoJSON file with exactly one feature of type polygon or multipolygon.
Castellum will then filter all subjects that live inside this (multi)polygon,
so it should enclose all areas where the conditions for recruitment are met.
Castellum will assume the Coordinate Reference System (CRS) of the GeoJSON file to be WGS 84 (EPSG:4326)
(https://tools.ietf.org/html/rfc7946#section-4).

### How to convert a shapefile to GeoJSON

Most Geographic Information Systems (GIS) such as QGIS or ArcGIS support this conversion out of the box.
Before exporting the GeoJSON file merge all polygons and multipolygons in the layer into one feature,
as the geofilter will fail if there is more than one feature in the file.
As mentioned above, the CRS of GeoJSON is by default WGS84. Desktop GIS applications should automatically reproject
the shapefile to WGS84 during the export to GeoJSON format, so this consideration really only applies if you
intend to build the GeoJSON file yourself
This is an example of a valid GeoJSON file:

```
  1 { "type": "Feature", "properties": { }, "geometry": { "type": "MultiPolygon", "coordinates": [ [ [ [ 13.3517429, 52.5189382 ], [ 13.2908489, 52.5165476 ], [ 13.346341, 52.4848593 ], [ 1    3.3512518, 52.446863 ], [ 13.3964313, 52.4785787 ], [ 13.4627272, 52.4504546 ], [ 13.4308069, 52.4893448 ], [ 13.4730399, 52.519237 ], [ 13.4141102, 52.5180417 ], [ 13.3821899, 52.56045    49 ], [ 13.3517429, 52.5189382 ] ] ] ] } }
```

### How to optimize GeoJSON for performance

The duration of the calculation scales roughly linearly to the number of vertices in the GeoJSON file.
If the calculation takes too long, try to reduce the number of vertices in the file.
This can be achieved in two ways:

-   Crop the spatial extent of your geographic data to the extent of the area where the subjects live (or at least most of them)
    This makes sense if most of your subjects are from the same city or state.
-   Generalize your polygon. This reduces the amount of vertices while retaining the general shape of the polygon.
    This makes sense of the resolution of your data is very high. Remember that Castellum derives the subjects' geolocations
    from their addresses, which refer to houses. Therefore, a polygon with a resolution of 10cm has no advantage over one with
    a resolution of 10m, as address data is resolved to 10m at best, as determined by typical house sizes.
