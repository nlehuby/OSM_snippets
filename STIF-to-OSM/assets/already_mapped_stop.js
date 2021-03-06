/*
	nlehuby
*/

var attr_osm = 'Map &copy; <a href="http://openstreetmap.org/">OpenStreetMap</a> contributors',
    attr_overpass = 'data from OSM, <a href="http://navitia.io/">navitia.io</a> and <a href="https://data.iledefrance-mobilites.fr">Opendata IDF Mobilités</a>';
var osm = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    opacity: 0.7,
    attribution: [attr_osm, attr_overpass].join(', ')
});

var map = new L.Map('map').addLayer(osm).setView(new L.LatLng(48.84702, 2.37705), 14);
L.control.scale().addTo(map);

var osm_stop_id = getParameterByName('osm_stop_id');
//var osm_stop_id = 472985886; //cas simple
//var osm_stop_id = 928458342; //cas avec plusieurs arrêts opendata

var tag_to_match = "ref:FR:STIF";


$(document).ready(function() {
    //authentification navitia
    $.ajaxSetup({
        beforeSend: function(xhr) {
            xhr.setRequestHeader("Authorization", "Basic " + btoa(navitia_api_key + ":"));
        }
    });

    get_osm_stop_info(osm_stop_id);

});

function get_navitia_stops_by_ref_id(ref_id) {
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/stop_points?filter=stop_point.has_code(ZDEr_ID_REF_A," + ref_id + ")",
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data);
            alert("Il y a eu un souci dans l'affichage des données opendata correspondant à cet arrêt")
        },
        success: function(data) {
            on_navitia_stops(data);
        }
    });
}

function get_navitia_routes_at_this_stop(stop_id, stop_name) {
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/stop_points/" + stop_id + "/routes?depth=2",
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data);
            alert("Il y a eu un souci dans l'affichage des données opendata correspondant à cet arrêt")
        },
        success: function(data) {
            on_navitia_routes_at_stop(data, stop_name);
        }
    });
}

relations_bus = {};

function get_osm_stop_info(stop_id) {
    url_op_bus = 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25];(node(' + stop_id + ');)->.a;rel(bn); out body;.a out body;';

    $.getJSON(url_op_bus, function(data) {
        geo = osmtogeojson(data);

        for (i = 0; i < geo.features.length; i++) {
            if (geo.features[i].properties['type'] == 'node') {
                bus_stop_id = geo.features[i].properties['id'];
                bus_stop_content = {};
                bus_stop_content.name = geo.features[i].properties.tags.name || '<i> pas de nom </i>';

                //récupération des parcours desservis d'après OSM
                relations_bus[bus_stop_id] = [];
                for (j = 0; j < geo.features[i].properties['relations'].length; j++) {
                    if (geo.features[i].properties['relations'][j]['reltags']['type'] == 'route') {
                        rel_name = `
                         <transport-thumbnail
                            data-transport-network="${geo.features[i].properties['relations'][j]['reltags']['network'] || ''}"
                            data-transport-mode="bus"
                            data-transport-line-code="${geo.features[i].properties['relations'][j]['reltags']['ref']|| ''}"
                            data-transport-line-color="${geo.features[i].properties['relations'][j]['reltags']['colour'] || 'white'}"
                            data-transport-destination="${geo.features[i].properties['relations'][j]['reltags']['to'] || '??'}">
                         </transport-thumbnail>
                        `
                        relations_bus[bus_stop_id].push({
                            'id': geo.features[i].properties['relations'][j]['rel'],
                            'name': rel_name
                        })
                    }
                }

                popup_content = "<h3>" + bus_stop_content.name + "</h3>";
                for (j = 0; j < relations_bus[bus_stop_id].length; j++) {
                    popup_content += relations_bus[bus_stop_id][j]['name'] + " <br> ";
                }

                document.getElementById("osm_stop_info").innerHTML = popup_content;
                popup_content += "<a href='http://osm.org/node/" + bus_stop_id + "' target='_blank'>Voir le détail</a>"
                geo.features[i].properties['popup_content'] = popup_content;

                var microcosm_link = "<a href='https://microcosm.5apps.com/opendata_bus.html?poi_type=bus_stop#18/"
                microcosm_link += geo.features[i].geometry.coordinates[1] + "/" + geo.features[i].geometry.coordinates[0]
                microcosm_link +=
                    microcosm_link += "' target='_blank'>Explorer la zone</a>"
                document.getElementById("microcosm_link").innerHTML = microcosm_link

                var ref_STIF_brut = geo.features[i].properties.tags[tag_to_match]
                document.getElementById("osm_ref_match").innerHTML = ref_STIF_brut || "pas encore de ref:FR:STIF";
                bus_stop_content.ref_STIF = ref_STIF_brut.split(";")
                for (var k = 0; k < bus_stop_content.ref_STIF.length; k++) {
                    get_navitia_stops_by_ref_id(bus_stop_content.ref_STIF[k])
                }

            }
        }

        bus_layer = L.geoJson(geo, {
            onEachFeature: function(feature, layer) {
                layer.bindPopup(feature.properties['popup_content'], {
                    maxWidth: 150
                });

                layer.setIcon(L.icon({
                    iconUrl: 'assets/img/blue_bus.png',
                    popupAnchor: [0, 0]
                }));
            },
        }).addTo(map);
        map.fitBounds(bus_layer.getBounds());
    });
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.href);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function on_navitia_stops(whole_navitia_info) {
    for (var k = 0; whole_navitia_info['stop_points'].length; k++) {
        stop_name = whole_navitia_info['stop_points'][k]['name'];
        stop_id = whole_navitia_info['stop_points'][k]['id'];
        stop_codes = whole_navitia_info['stop_points'][k]['codes'];
        for (j = 0; j < stop_codes.length; j++) {
            if (stop_codes[j]['type'] == "ZDEr_ID_REF_A") {
                stop_ref_opendata = stop_codes[j]['value']
            }
        }
        stop_name += " - ref:FR:STIF : " + stop_ref_opendata;

        get_navitia_routes_at_this_stop(stop_id, stop_name)

        nav_img = L.icon({
            iconUrl: 'assets/img/black_bus.png',
            popupAnchor: [0, 0]
        });
        stop_marker = L.marker([whole_navitia_info['stop_points'][k]['coord']['lat'], whole_navitia_info['stop_points'][k]['coord']['lon']], {
            icon: nav_img
        });
        stop_marker.addTo(map).bindPopup('<h3>' + stop_name + '</h3><div><a href="http://canaltp.github.io/navitia-playground/play.html?request=api.navitia.io/v1/coverage/fr-idf/stop_points/' + stop_id + '" target="_blank"> voir le détail</a></div>');
    }
}

function on_navitia_routes_at_stop(whole_navitia_info, stop_name) {
    route_id = whole_navitia_info['routes'][0]['id']

    routes_at_stop = []
    for (j = 0; j < whole_navitia_info['routes'].length; j++) {
        var network = whole_navitia_info['routes'][j]['line']['network']['name'];
        var line_code = whole_navitia_info['routes'][j]['line']['code'];
        var line_color =  "#" + whole_navitia_info['routes'][j]['line']['color'];
        var line_destination = whole_navitia_info['routes'][j]['direction']['name'];
        var route_name = `
         <transport-thumbnail
            data-transport-network="${ network || ''}"
            data-transport-mode="bus"
            data-transport-line-code="${ line_code || ''}"
            data-transport-line-color="${ line_color || 'white'}"
            data-transport-destination="${ line_destination || '??'}">
         </transport-thumbnail>
        `
        routes_at_stop.push(route_name)
    }

    to_text = "<h3>" + stop_name + "</h3>"
    for (j = 0; j < routes_at_stop.length; j++) {
        to_text += routes_at_stop[j] + " <br> ";
    }

    var opendata_list = document.getElementById("opendata_stop_info");
    var listing = opendata_list.appendChild(document.createElement('div'));
    listing.innerHTML = to_text;
}
