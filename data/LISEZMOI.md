Déposez ici le GeoJSON officiel des blocs , une Feature par bloc avec la propriété `code` (ex. "CI-101"),
puis lancez :  python manage.py load_amont --geojson data/blocs_officiels.geojson
Un export shapefile peut être converti avec QGIS (Exporter > GeoJSON, SCR EPSG:4326).
