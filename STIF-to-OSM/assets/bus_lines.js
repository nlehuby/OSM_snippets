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

//var osm_relation_code = 3315943;
//var line_commercial_code = '12';

var osm_relation_code = getParameterByName('osm_relation');
var line_commercial_code = getParameterByName('line_code');

var tag_to_match = "ref:FR:STIF:ExternalCode_Line";
var selected_navitia_line_index = 0;
var navitia_lines_data = "";
var navitia_line_geojson = []

document.getElementById("link_to_route_choose").style.display = 'none';
var next_navitia_candidate_button = document.getElementById("next_navitia_candidate_button");
next_navitia_candidate_button.onclick = function() {
    selected_navitia_line_index += 1;
    if (navitia_lines_data['lines'][selected_navitia_line_index] == undefined) {
        selected_navitia_line_index = 0;
    }
    document.getElementById("navitia_current_line").innerHTML = selected_navitia_line_index + 1;
    display_navitia_info(navitia_lines_data['lines'][selected_navitia_line_index]);
    display_navitia_stops(navitia_lines_data['lines'][selected_navitia_line_index]['id']);
}

var add_navitia_ref_to_osm = document.getElementById("add_navitia_ref_to_osm");
add_navitia_ref_to_osm.onclick = function() {
    if (!auth.authenticated()) {
        alert("Vous n'êtes pas connecté à OSM ! Utilisez le bouton en haut de la page d'accueil puis réessayez.")
    }
    var navitia_ref;
    //on retrouve le code à envoyer
    for (i = 0; i < navitia_lines_data['lines'][selected_navitia_line_index]['codes'].length; i++) {
        if (navitia_lines_data['lines'][selected_navitia_line_index]['codes'][i]['type'] == 'source') {
            navitia_ref = navitia_lines_data['lines'][selected_navitia_line_index]['codes'][i]['value'];
        }
    }
    var navitia_line_id = navitia_lines_data['lines'][selected_navitia_line_index]['id']

    if (navitia_ref != undefined) {
        send_navitia_ref_to_openstreetmap(navitia_ref, osm_relation_code, navitia_line_id);
    } else {
        console.log("impossible de trouver le code à envoyer à OSM")
    }
}

$(document).ready(function() {
    //authentification navitia
    $.ajaxSetup({
        beforeSend: function(xhr) {
            xhr.setRequestHeader("Authorization", "Basic " + btoa(navitia_api_key + ":"));
        }
    });

    get_osm_line_info(osm_relation_code);
    if (line_commercial_code) {
        get_navitia_lines_candidates(line_commercial_code);
    }
});

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.href);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function send_navitia_ref_to_openstreetmap(navitia_ref, osm_relation_id, navitia_line_id) {
    var relation_xml = get_node_or_way(osm_relation_id, 'relation'); //mouais, va ptet falloir changer le nom de la fonction dans la lib quand même ...
    edit_tag(relation_xml, 'relation', tag_to_match, navitia_ref)

    function after_osm_modif() {
        document.location.href = "./route_choose.html?osm_line_id=" + osm_relation_id + "&navitia_line_id=" + navitia_line_id
    }
    send_data_to_osm(relation_xml, osm_relation_id, "relation", "Ajout de référence opendata STIF sur les lignes", after_osm_modif)
}

function get_navitia_lines_candidates(line_code) {
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/lines?filter=line.code%3D" + line_commercial_code,
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log("Il y a eu un souci dans l'affichage des données opendata candidates")
        },
        success: function(data) {
            on_navitia_lines_candidates(data);
        }
    });
}

function get_navitia_lines_by_ref_id(ref_id) {
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/lines?filter=line.has_code(source," + ref_id + ")",
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data);
            alert("Il y a eu un souci dans l'affichage des données opendata correspondantes")
        },
        success: function(data) {
            get_opendata_lines_tracks_by_ref_id(ref_id)
            on_navitia_lines_candidates(data);
        }
    });
}

function get_opendata_lines_tracks_by_ref_id(ref_id) {
    tt_ref = ref_id.split(':')[0]
    //si on utilise $.ajax ici, on passera les clefs d'authentification navitia :(
    fetch("https://data.iledefrance-mobilites.fr/api/v2/catalog/datasets/bus_lignes/records?rows=1&search=" + tt_ref)
        .then(function(data) {
            return data.json()
        })
        .then(function(response) {
            opendata_geojson = response['records'][0]['record']['fields']['geo_shape']
            var opendata_style = {
                "color": "black",
                "weight": 5,
                "opacity": 0.65
            };
            relation_opendata = L.geoJson(opendata_geojson, {
                style: opendata_style
            }).addTo(map);
        })
        .catch(function(error) {
            console.log("Il y a eu un souci dans l'affichage du tracés de ligne opendata correspondant " + error.message);
        });
}

function on_navitia_lines_candidates(whole_navitia_info) {
    navitia_lines_data = whole_navitia_info;
    selected_navitia_line_index = 0;
    display_navitia_info(whole_navitia_info['lines'][selected_navitia_line_index]);
    display_navitia_stops(whole_navitia_info['lines'][selected_navitia_line_index]['id']);
    document.getElementById("navitia_lines_count").innerHTML = whole_navitia_info['pagination']['total_result'];
    if (whole_navitia_info['pagination']['total_result'] == "1") {
        document.getElementById('next_navitia_candidate_button').style.display = 'none';
        var link_to_route_choose = document.getElementById('link_to_route_choose')
        link_to_route_choose.style.display = 'block';
        link_to_route_choose.href = "./route_choose.html?osm_line_id=" + osm_relation_code + "&navitia_line_id=" + whole_navitia_info['lines'][0]['id']
    }
}

function display_navitia_info(navitia_line_info) {
    document.getElementById("navitia_line_name").innerHTML = navitia_line_info['name'];
    document.getElementById("navitia_line_code").innerHTML = navitia_line_info['code'];
    document.getElementById("navitia_line_route").innerHTML = navitia_line_info['routes'][0]['name'];
    document.getElementById("navitia_line_mode").innerHTML = navitia_line_info['commercial_mode']['name'];
    document.getElementById("navitia_line_network").innerHTML = navitia_line_info['network']['name'];
    document.getElementById("navitia_line_color").style = "width:20px;height:20px;background:#" + navitia_line_info['color'] + ";";
    //TODO : mettre des liens navitia playground
}

function display_navitia_stops(navitia_line_id) {
    for (var i in navitia_line_geojson) {
        map.removeLayer(navitia_line_geojson[i]);
    }
    navitia_line_geojson = [];
    //affichage des arrêts navitia
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/lines/" + navitia_line_id + "/stop_points?count=500",
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data)
        },
        success: function(data) {
            nav_img = L.icon({
                iconUrl: 'assets/img/black_bus.png',
                popupAnchor: [0, 0]
            });

            for (i = 0; i < data['stop_points'].length; i++) {
                stop_name = data['stop_points'][i]['name'];
                stop_code = data['stop_points'][i]['id'];
                stop_marker = L.marker([data['stop_points'][i]['coord']['lat'], data['stop_points'][i]['coord']['lon']], {
                    icon: nav_img
                });
                navitia_line_geojson.push(stop_marker);
                stop_marker.addTo(map).bindPopup('<h3>' + stop_name + '</h3><div><a href="http://canaltp.github.io/navitia-playground/play.html?request=api.navitia.io/v1/coverage/fr-idf/stop_points/' + stop_code + '" target="_blank"> voir le détail</a></div>');
            }
        }
    });
}

function get_osm_line_info(relation_id) {
    //affichage de la ligne OSM
    $.ajax({
        url: 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25];relation(' + osm_relation_code + ');(._;>>;);out;',
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data);
            alert("Il y a eu un souci dans l'affichage des données osm");
        },
        success: function(data) {
            //on retrouve la relation en question
            var relation = data.elements.reverse()[0];
            for (i = 0; i < data['elements'].length; i++) {
                if (data['elements'][i]['id'] == relation_id) {
                    relation = data['elements'][i];
                }
            }
            //affichage des tags OSM
            document.getElementById("osm_line_name").innerHTML = relation['tags']['name'] ? relation['tags']['name'] : "<i>Pas de nom renseigné</i>";
            document.getElementById("osm_line_mode").innerHTML = relation['tags']['route_master'] ? relation['tags']['route_master'] : "<i style='color:red;'>Pas de mode renseigné</i>";
            document.getElementById("osm_line_network").innerHTML = relation['tags']['network'] ? relation['tags']['network'] : "<i style='color:red;'>tag network non renseigné</i>";
            document.getElementById("osm_line_operator").innerHTML = relation['tags']['operator'] ? relation['tags']['operator'] : "<i style='color:red;'>tag operator non renseigné</i>";
            document.getElementById("osm_line_color").style = "width:20px;height:20px;background:" + relation['tags']['colour'] + ";";

            //TODO : mettre des liens OSM
            var is_there_a_match = document.getElementById("osm_ref_match");
            is_there_a_match.innerHTML = "Pas d'association"
            if (relation['tags'][tag_to_match] != undefined) {
                is_there_a_match.innerHTML = "Association OK"
                get_navitia_lines_by_ref_id(relation['tags'][tag_to_match]);
                document.getElementById('add_navitia_ref_to_osm').style.display = 'none';
            }
            //transformation en geojson
            geo = osmtogeojson(data);

            // marqueur pour les éléments qu'on ne veut pas voir
            var geojsonBlankMarkerOptions = {
                radius: 8,
                fillColor: "#ff7800",
                color: "#000",
                weight: 0,
                opacity: 0,
                fillOpacity: 0
            };

            // marqueur pour les stop_position
            var geojsonMarkerOptions = {
                radius: 10,
                fillColor: "blue",
                color: "blue",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            };

            //fonction qui transforme les points du geojson en qqch d'affichable
            function DisplayOSMBusStops(feature, latlng) {
                if (feature.properties['type'] == 'node') {
                    if (feature.properties['tags']['highway'] == 'bus_stop') {
                        //console.log(feature.properties)
                        var myicon = L.icon({
                            iconUrl: 'assets/img/blue_bus.png',
                        });
                        return L.marker(latlng, {
                            icon: myicon
                        })
                    } else if (feature.properties['tags']['public_transport'] == 'stop_position') {
                        return L.circleMarker(latlng, geojsonMarkerOptions)
                    } else {
                        return L.circleMarker(latlng, geojsonBlankMarkerOptions)
                    }
                }
            }

            //fonction qui affine les propriétés du geosjon
            function onEachFeature(feature, layer) {
                if (feature.properties['type'] == 'node') {
                    if (feature.properties['tags']['highway'] == 'bus_stop' || feature.properties['tags']['public_transport'] == 'stop_position') {
                        layer.bindPopup(feature.properties.tags.name + '<br><a href="http://www.openstreetmap.org/node/' + feature.properties['id'] + '" target="_blank">Voir sur OSM</a>');
                    }
                }
                if (feature.properties['type'] == 'way') {
                    layer.setStyle({
                        "color": "blue"
                    });
                }
            }

            //affichage du geojson
            relation_OSM = L.geoJson(geo, {
                onEachFeature: onEachFeature,
                pointToLayer: DisplayOSMBusStops
            }).addTo(map);
            map.fitBounds(relation_OSM.getBounds());

        }
    });
}
