Geo Filters
===========

If that feature has been activated on the server, Castellum also allows to
filter by geographical properties of a subject's address.

.. admonition:: Example

    If the desired participants for a study should be older than 40 years
    and live in an area where the noise from an airport is over 40dB you
    would create and upload a GeoJSON file with a (multi)polygon spanning
    the area where this condition applies. Afterwards proceed as usual with
    setting the filter for age in the study filter UI. The resulting
    subjects in the recruitment interface match the filter condition AND
    their contact address is located inside the uploaded polygon.

GeoJSON format
--------------

To use this, you need to provide a valid `GeoJSON
<https://tools.ietf.org/html/rfc7946>`__ file with a either a single feature or
a feature collection of type “Polygon” or “MultiPolygon”. Castellum will then
filter all subjects that live inside this (multi)polygon, so it should enclose
all areas where the conditions for recruitment are met. Note that the
Coordinate Reference System (CRS) must be WGS84 (EPSG:4326).

This is an example of a valid GeoJSON file::

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

http://geojson.io is a simple tool to preview and edit GeoJSON.

How to convert a shapefile to GeoJSON
-------------------------------------

Most Geographic Information Systems (GIS) such as QGIS or ArcGIS support
the conversion to GeoJSON out of the box. Desktop GIS applications
should automatically reproject the shapefile to WGS84 during the export
to GeoJSON format.

Optimize GeoJSON for performance
--------------------------------

The duration of the calculation scales roughly linearly to the number of
vertices in the GeoJSON file. If the calculation takes too long, try to
reduce the number of vertices in the file. This can be achieved in two
ways:

-  Crop the spatial extent of your geographic data to the extent of the
   area where the subjects live (or at least most of them). This makes
   sense if most of your subjects are from the same city or state.
-  Generalize your polygon. This reduces the amount of vertices while
   retaining the general shape of the polygon. This makes sense of the
   resolution of your data is very high. Remember that Castellum derives
   the subjects’ geolocations from their addresses, which refer to
   houses. Therefore, a polygon with a resolution of 10cm has no
   advantage over one with a resolution of 10m, as address data is
   resolved to 10m at best, as determined by typical house sizes.
