/*
	nlehuby
*/

var attr_osm = 'Map data &copy; <a href="http://openstreetmap.org/">OpenStreetMap</a> contributors',
    attr_overpass = 'stops from <a href="http://www.overpass-api.de/">Overpass API</a> and <a href="http://navitia.io/">navitia.io</a>';
var osm = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    opacity: 0.7,
    attribution: [attr_osm, attr_overpass].join(', ')
});

var map = new L.Map('map').addLayer(osm).setView(new L.LatLng(48.84702, 2.37705), 18);
L.control.scale().addTo(map);

var osm_route_id = getParameterByName('osm_route_id');
var navitia_route_id = getParameterByName('navitia_route_id');
// var osm_route_id = 1103965;
// var navitia_route_id = 'route:OIF:014014011:11';

var tag_to_match = "ref:FR:STIF";

var osm_stop_list = []
var navitia_stop_list = []

var current_osm_stop_index = 0;

var next_osm_stop_button = document.getElementById("next_osm_stop_button");
next_osm_stop_button.onclick = skip_to_next_osm;

var add_one_navitia_ref_to_osm = document.getElementById("add_navitia_one_ref_to_osm");
add_one_navitia_ref_to_osm.onclick = function() {
    add_navitia_ref_to_osm("one");
}
var add_two_navitia_ref_to_osm = document.getElementById("add_navitia_two_ref_to_osm");
add_two_navitia_ref_to_osm.onclick = function() {
    add_navitia_ref_to_osm("two");
}

$(document).ready(function() {
    //authentification navitia
    $.ajaxSetup({
        beforeSend: function(xhr) {
            xhr.setRequestHeader("Authorization", "Basic " + btoa(navitia_api_key + ":"));
        }
    });

    get_osm_info_for_this_route(osm_route_id);
});

function get_osm_info_for_this_route(osm_relation_route_id) {
    // on vérifie si c'est du transport v1 ou v2
    $.ajax({
        url: 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; relation(' + osm_relation_route_id + ');out tags;',
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data)
        },
        success: function(data) {
            var params_appel = []
            for (i = 0; i < data['elements'].length; i++) {
                relation_data = data['elements'][i]
                if (relation_data['tags']['public_transport:version'] == "2") {
                    params_appel.push({
                        'id': relation_data['id'],
                        'role': 'platform'
                    })
                } else if (relation_data['tags']['public_transport:version'] == "1") {
                    params_appel.push({
                        'id': relation_data['id'],
                        'role': 'stop'
                    })
                } else {
                    alert("Le tag public_transport:version n'est pas renseigné. Il est pourtant nécessaire pour récupérer les arrêts de ce parcours !");
                    document.location.href = "http://makinacorpus.github.io/osm-transport-editor/#/" + osm_route_id;
                }
            }
            get_stops_from_osm_routes(params_appel)
        }
    });
}

function get_stops_from_osm_routes(array_with_routes_and_roles) {
    // on reconstruit un appel overpass pour récupérer tous les arrêts des parcours, avec les rôles qu'on a déterminé précédemment

    //[out:json][timeout:25]; (relation(1103949);node(r:"stop");)->.a;rel(bn);out body;.a out body; (relation(1103948);node(r:"stop");)->.a;rel(bn);out body;.a out body;
    var url_overpass = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; ";
    for (i = 0; i < array_with_routes_and_roles.length; i++) {
        url_overpass += '(relation(' + array_with_routes_and_roles[i]['id'] + ');node(r:"' + array_with_routes_and_roles[i]['role'] + '");)->.a;rel(bn);out body;.a out body;'
    }

    $.getJSON(url_overpass, function(data) {
        geo = osmtogeojson(data);
        for (i = 0; i < geo.features.length; i++) {
            if (geo.features[i].properties['type'] == 'node') {
                var stop_content = {}
                stop_content['id'] = geo.features[i].properties['id'];
                stop_content['name'] = geo.features[i].properties.tags.name || '<i> pas de nom </i>';
                stop_content['ref'] = geo.features[i].properties.tags[tag_to_match]
                stop_content['lat'] = geo.features[i]['geometry']['coordinates'][1]
                stop_content['lon'] = geo.features[i]['geometry']['coordinates'][0]

                //récupération des parcours desservis d'après OSM
                stop_content['relations'] = "";
                var deduplicate = [];
                for (j = 0; j < geo.features[i].properties['relations'].length; j++) {
                    if (geo.features[i].properties['relations'][j]['reltags']['type'] == 'route') {
                        rel_name = '[' + (geo.features[i].properties['relations'][j]['reltags']['network'] || '') + '] '
                        rel_name += geo.features[i].properties['relations'][j]['reltags']['ref'] + ' > ' + geo.features[i].properties['relations'][j]['reltags']['to']
                        rel_name += '<br/>'
                        if (deduplicate.indexOf(geo.features[i].properties['relations'][j]['rel']) == -1) {
                            deduplicate.push(geo.features[i].properties['relations'][j]['rel'])
                            stop_content['relations'] += rel_name
                        }
                    }
                }
                osm_stop_list.push(stop_content)
            }
        }

        console.log(osm_stop_list)

        //maintenant qu'on a les arrêts OSM, on récupère les arrêts navitia
        get_stops_from_navitia_route(navitia_route_id)
    });

}

function get_stops_from_navitia_route(navitia_route_id) {
    //on récupère tous les arrêts du parcours navitia
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/routes/" + navitia_route_id + "/stop_points?count=500",
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data)
        },
        success: function(data) {

            for (i = 0; i < data['stop_points'].length; i++) {
                var stop_content = {}
                stop_content['id'] = data['stop_points'][i]['id'];
                stop_content['name'] = data['stop_points'][i]['name'];
                stop_content['ref'] = ""
                for (j = 0; j < data['stop_points'][i]['codes'].length; j++) {
                    if (data['stop_points'][i]['codes'][j]['type'] == "ZDEr_ID_REF_A") {
                        stop_content['ref'] = data['stop_points'][i]['codes'][j]['value']
                    }
                }
                stop_content['lat'] = data['stop_points'][i]['coord']['lat']
                stop_content['lon'] = data['stop_points'][i]['coord']['lon']
                navitia_stop_list.push(stop_content)
            }
            console.log(navitia_stop_list)

            // on a maintenant le nécessaire pour commencer à mapper :)
            display_one_osm_stop(0)
        }
    });
}

function display_one_osm_stop(stop_index) {
    //affiche les tags de l'arrêt OSM et l'affiche sur la carte
    osm_stop = osm_stop_list[stop_index]
    var to_html = "<h3>" + osm_stop.name + "</h3>";
    to_html += osm_stop.relations
    document.getElementById("osm_stop_info").innerHTML = to_html;

    to_html_ = "<a href='./stop.html?osm_stop_id=" + osm_stop.id + "' target='_blank'> <i>Voir toutes les ref:FR:STIF de cet arrêt</i></a>"

    document.getElementById("osm_ref_match").innerHTML = to_html_;

    stop_img = L.icon({
        iconUrl: 'assets/img/blue_bus.png',
        popupAnchor: [0, 0]
    });
    stop_marker = L.marker([osm_stop['lat'], osm_stop['lon']], {
        icon: stop_img
    });
    stop_marker.addTo(map).bindPopup("OSM " + to_html + "<br>ref:FR:STIF : " + (osm_stop.ref || "<i>Pas de ref:FR:STIF</i>"));
    map.panTo([osm_stop['lat'], osm_stop['lon']]);

    display_navitia_candidates_for_this_stop(osm_stop)
}


function display_navitia_candidates_for_this_stop(osm_stop_info) {
    //trier les arrêts navitia par distance par rapport au point osm
    var position = turf.point([osm_stop_info.lon, osm_stop_info.lat]);
    navitia_stop_list.sort(function(a, b) {
        var locA = turf.point([a.lon, a.lat]);
        var locB = turf.point([b.lon, b.lat]);

        var distanceA = turf.distance(position, locA, 'kilometers');
        var distanceB = turf.distance(position, locB, 'kilometers');
        return distanceA - distanceB;
    });

    //afficher les deux plus proches
    display_one_navitia_stop(0, "opendata_stop_one_info");
    display_one_navitia_stop(1, "opendata_stop_two_info");
}

function display_one_navitia_stop(stop_index, placeholder) {
    //récupère les parcours desservis, puis affiche les infos
    var navitia_stop = navitia_stop_list[stop_index]
    console.log(navitia_stop)
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/routes/" + navitia_route_id + "/stop_points/" + navitia_stop.id + "/routes?depth=2",
        dataType: 'json',
        global: true,
        error: function(data) {
            console.log(data);
            alert("Il y a eu un souci dans l'affichage des données opendata correspondant à cet arrêt")
        },
        success: function(data) {
            console.log(navitia_stop)
            var to_html = "<h3>" + navitia_stop.name + "<br>(ref:FR:STIF : " + navitia_stop.ref + ")";
            if (navitia_stop.ref == osm_stop.ref) {
                to_html += "<span class='icon fa-check-circle'></span>";
            }
            to_html += "</h3>";

            for (j = 0; j < data['routes'].length; j++) {
                var network = data['routes'][j]['line']['network']['name'];
                var line_code = data['routes'][j]['line']['code'];
                var line_destination = data['routes'][j]['direction']['name'];

                var route_name = "[" + network + "] " + line_code + " > " + line_destination;
                to_html += route_name + "<br>"
            }

            document.getElementById(placeholder).innerHTML = to_html;

            stop_img = L.icon({
                iconUrl: 'assets/img/black_bus.png',
                popupAnchor: [0, 0]
            });
            stop_marker = L.marker([navitia_stop['lat'], navitia_stop['lon']], {
                icon: stop_img
            });
            stop_marker.addTo(map).bindPopup('opendata' + to_html);
        }
    });

}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.href);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function send_navitia_ref_to_openstreetmap(navitia_ref, osm_node_id, callback) {
    var stop_xml = get_node_or_way(osm_node_id, 'node');
    edit_tag(stop_xml, 'node', tag_to_match, navitia_ref)
    send_data_to_osm(stop_xml, osm_node_id, "node", "Ajout de référence opendata STIF sur les arrêts", callback)
}

function skip_to_next_osm(changeset_id, junk) {
    current_osm_stop_index += 1;
    if (osm_stop_list[current_osm_stop_index] == undefined) {
        current_osm_stop_index = 0;
        notify_user()
    }
    display_one_osm_stop(current_osm_stop_index);
}

function add_navitia_ref_to_osm(one_or_two) {
    var current_navitia_stop_index = 1;
    if (one_or_two == "one") {
        current_navitia_stop_index = 0;
    }
    var navitia_ref = navitia_stop_list[current_navitia_stop_index]['ref'];
    var osm_stop_id = osm_stop_list[current_osm_stop_index]['id']


    var osm_refs_to_contribute = navitia_ref;

    if (osm_stop_list[current_osm_stop_index]['ref']) {
        var osm_refs = osm_stop_list[current_osm_stop_index]['ref'].split(';')

        if (osm_refs.indexOf(navitia_ref) != -1) { // si la nvelle ref est déjà dans OSM
            console.log("cette ref est déjà dans OSM")
            skip_to_next_osm();
            return;
        }
        osm_refs.push(navitia_ref);

        osm_refs_to_contribute = osm_refs.join(';');

    }

    if (navitia_ref != "") {
        send_navitia_ref_to_openstreetmap(osm_refs_to_contribute, osm_stop_id, skip_to_next_osm);
    } else {
        console.log("impossible de trouver le code à envoyer à OSM / code déjà dans OSM, pas de modif")
        skip_to_next_osm()
    }
}

function notify_user() {
    alert("Vous avez fait le tour de cette ligne ! Pourquoi ne pas ré-ordonner ses arrêts maintenant ?")
}
