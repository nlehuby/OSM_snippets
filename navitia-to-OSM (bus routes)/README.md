navitia > OSM : aide à la carto des lignes de bus
============================================================

Quelques morceaux de scripts autour d'OpenStreetMap

.
├── collecte
│   └── analyse
├── collect_osm_relations.py
├── default_params
│   └── __init__.py
├── params
│   └── __init__.py <-- TODO
├── rapprochement
├── rapprochement_osm_navitia.py
├── README.md
├── rendu
│   └── assets
│       ├── api.js
│       ├── auth.js <-- TODO
│       ├── nav_auth.js <-- TODO
│       ├── black_bus.png
│       ├── default.auth.js
│       ├── default.nav_auth.js
│       ├── navitia_bus.png
│       ├── OverPassLayer.js
│       ├── red_bus.png
│       ├── template.html
│       └── template_liste.html
└── route_to_html.py

Étape 1 - collecter des relations OSM
fichier collect_osm_relations.py

Étape 2 - trouver les parcours navitia correspondantes
fichier rapprochement_osm_navitia.py

Étape 3 - afficher les deux sur une même page pour analyses et comparaisons
fichier route_to_html.py
