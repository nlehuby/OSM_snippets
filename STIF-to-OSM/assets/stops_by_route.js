/*
	nlehuby
*/



var osm_route_id = getParameterByName('osm_route_id');
var navitia_route_id = getParameterByName('navitia_route_id');
//var osm_route_id = 1103965;
//var navitia_route_id = 'route:OIF:014014011:11';

var tag_to_match = "ref:FR:STIF";
var JOSM_url_base = "https://localhost:8112/load_object?objects="
main()

function find_opendata_closer_stop(osm_stop_pos, opendata_stops) {
    var sorted_opendata_stops = opendata_stops.sort(function(a, b) {
        var locA = turf.point([a.lon, a.lat]);
        var locB = turf.point([b.lon, b.lat]);

        var distanceA = turf.distance(osm_stop_pos, locA, 'kilometers');
        var distanceB = turf.distance(osm_stop_pos, locB, 'kilometers');
        return distanceA - distanceB;
    })
    return {
        'opendata_candidate': sorted_opendata_stops[0],
        'distance': turf.distance(osm_stop_pos, turf.point([sorted_opendata_stops[0].lon, sorted_opendata_stops[0].lat]), 'kilometers') * 1000
    }
}

async function main() {
    var osm_stop_list = await get_osm_info(osm_route_id);
    var opendata_stops = await get_navitia_info(navitia_route_id)

    function extract_ref(elem) {
        return elem['ref'];
    }

    var ref_ok = opendata_stops['opendata_ok'].map(extract_ref);
    var rek_ko = opendata_stops['opendata_ko'].map(extract_ref);

    var stops_div = document.getElementById("stops_details")

    osm_stop_list.forEach(function(current_osm_stop) {

        var balise = document.createElement("DT");
        balise.innerHTML=`<a href='stop.html?osm_stop_id=${current_osm_stop['id']}' target='_blank'>${current_osm_stop['name']}</a>`
        stops_div.appendChild(balise);
        var balise_ext = document.createElement("DD");


        var osm_location = turf.point([current_osm_stop['lon'], current_osm_stop['lat']]);

        if (!current_osm_stop['ref']) {
            var opendata_candidate = find_opendata_closer_stop(osm_location, opendata_stops['opendata_ok'])
            var ref_to_add = opendata_candidate['opendata_candidate']['ref']

            balise_ext.innerHTML=`
            <p>
            pas encore de ref:FR:STIF <br/>
            <span class="icon fa-child"></span>
            <span class="icon fa-child"></span>
            proposition ${opendata_candidate['opendata_candidate']['name']} à ${opendata_candidate['distance']} mètres
            <span class="icon fa-child"></span>
            <span class="icon fa-child"></span><br/>
            <a onclick="send_to_josm('${current_osm_stop['id']}','${ref_to_add}')">Ajouter dans JOSM</a>
            </p>
            `
            stops_div.appendChild(balise_ext);

        } else {
            var refs = current_osm_stop['ref'].split(';')
            var found_match = false;
            balise_ext.innerHTML=""
            refs.forEach(function(one_ref) {
                if (ref_ok.includes(one_ref)) {
                    found_match = true;
                    var opendata_match = opendata_stops['opendata_ok'].filter(function has_this_ref(elem) {
                        return elem['ref'] == one_ref
                    })
                    var opendata_location = turf.point([opendata_match[0]['lon'], opendata_match[0]['lat']]);
                    var distance = turf.distance(osm_location, opendata_location, 'kilometers');

                    balise_ext.innerHTML+=`
                    <p>
                    ref:FR:STIF ${one_ref} <span class="icon fa-check-circle"></span><br/>
                    arrêt opendata : ${opendata_match[0]['name']}, à ${distance * 1000} m
                    </p>
                    `

                } else if (rek_ko.includes(one_ref)) {
                    balise_ext.innerHTML+=`
                    <p>
                    <span class="icon fa-bug"></span>
                    Ce ref:FR:STIF ${one_ref} appartient à cette ligne mais dans la direction opposée !!
                    <span class="icon fa-bug"></span> <br/>
                    <a onclick="send_to_josm('${current_osm_stop['id']}')">Charger cet arrêt dans JOSM</a>
                    </p>
                    `
                } else {
                    balise_ext.innerHTML+=`
                    <p>
                    ref:FR:STIF ${one_ref} d'une autre ligne <br/>
                    </p>
                    `
                }
            });
            if (!found_match){
                var opendata_candidate = find_opendata_closer_stop(osm_location, opendata_stops['opendata_ok'])
                var ref_to_add = current_osm_stop['ref'] + ";" + opendata_candidate['opendata_candidate']['ref']
                balise_ext.innerHTML+=`
                <p>
                <span class="icon fa-child"></span>
                <span class="icon fa-child"></span>
                proposition ${opendata_candidate['opendata_candidate']['name']} à ${opendata_candidate['distance']} mètres
                <span class="icon fa-child"></span>
                <span class="icon fa-child"></span>
                <br/>
                <a onclick="send_to_josm('${current_osm_stop['id']}','${ref_to_add}')">Ajouter dans JOSM</a>
                </p>
                `
            }
            stops_div.appendChild(balise_ext);
        }
    });
}

async function get_osm_info() {
    //TODO : aussi récupérer de quoi afficher des infos sur le parcours
    var stops_params = await get_osm_info_for_this_route(osm_route_id);
    var osm_stop_list = await get_stops_from_osm_routes(stops_params);

    function has_ref(element) {
        return (element['ref'] !== undefined);
    }
    var stops_with_ref = osm_stop_list.filter(has_ref);

    var ref_count = document.createElement("P");
    var t = document.createTextNode(`${stops_with_ref.length} arrêts sur ${osm_stop_list.length} ont un code STIF`);
    ref_count.appendChild(t);
    document.getElementById("route_info").appendChild(ref_count);

    return osm_stop_list

}

async function get_navitia_info() {

    if (navitia_route_id.substr(-2) === "_R" ) {
        var navitia_opposite_route_id = navitia_route_id.substring(0, navitia_route_id.length - 2)
    } else {
        var navitia_opposite_route_id = navitia_route_id + '_R'
    }

    var navitia_stop_list = await get_stops_from_navitia_route(navitia_route_id);
    var navitia_wrong_stop_list = await get_stops_from_navitia_route(navitia_opposite_route_id) || [];
    return {
        'opendata_ok': navitia_stop_list,
        'opendata_ko': navitia_wrong_stop_list
    }
}

async function get_osm_info_for_this_route(osm_relation_route_id) {
    // on vérifie si c'est du transport v1 ou v2
    try {
        var overpass_url = 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; relation(' + osm_relation_route_id + ');out tags;'
        var overpass_response = await fetch(overpass_url);
        var overpass_data = await overpass_response.json();

        var params_appel = []
        for (i = 0; i < overpass_data['elements'].length; i++) {
            var relation_data = overpass_data['elements'][i]
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
        return (params_appel)

    } catch (err) {
        console.log("erreur en récupérant les infos de la ligne sur OSM via Overpass : " + err)
    }
}

async function get_stops_from_osm_routes(array_with_routes_and_roles) {
    // on reconstruit un appel overpass pour récupérer tous les arrêts des parcours, avec les rôles qu'on a déterminé précédemment
    try {
        //[out:json][timeout:25]; (relation(1103949);node(r:"stop");)->.a;rel(bn);out body;.a out body; (relation(1103948);node(r:"stop");)->.a;rel(bn);out body;.a out body;
        var overpass_url = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; ";
        for (i = 0; i < array_with_routes_and_roles.length; i++) {
            overpass_url += '(relation(' + array_with_routes_and_roles[i]['id'] + ');node(r:"' + array_with_routes_and_roles[i]['role'] + '");)->.a;rel(bn);out body;.a out body;'
        }

        var overpass_response = await fetch(overpass_url);
        var overpass_data = await overpass_response.json();

        var stop_list = []
        var geo = osmtogeojson(overpass_data);
        for (var i = 0; i < geo.features.length; i++) {
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
                stop_list.push(stop_content)
            }
        }

        return stop_list



    } catch (err) {
        console.log("erreur en récupérant les infos de la ligne sur OSM via Overpass : " + err)
    }

}

async function get_stops_from_navitia_route(navitia_route_id) {
    //on récupère tous les arrêts du parcours navitia
    try {
        var navitia_url = "https://api.navitia.io/v1/coverage/fr-idf/routes/" + navitia_route_id + "/stop_points?count=500";
        var navitia_response = await fetch(navitia_url, {
            headers: {
                "Authorization": "Basic " + btoa(navitia_api_key + ":")
            },
        });
        var navitia_data = await navitia_response.json();

        var stop_list = []

        for (var i = 0; i < navitia_data['stop_points'].length; i++) {
            var stop_content = {}
            stop_content['id'] = navitia_data['stop_points'][i]['id'];
            stop_content['name'] = navitia_data['stop_points'][i]['name'];
            stop_content['ref'] = ""
            for (j = 0; j < navitia_data['stop_points'][i]['codes'].length; j++) {
                if (navitia_data['stop_points'][i]['codes'][j]['type'] == "ZDEr_ID_REF_A") {
                    stop_content['ref'] = navitia_data['stop_points'][i]['codes'][j]['value']
                }
            }
            stop_content['lat'] = navitia_data['stop_points'][i]['coord']['lat']
            stop_content['lon'] = navitia_data['stop_points'][i]['coord']['lon']
            stop_list.push(stop_content)
        }
        return (stop_list)

    } catch (err) {
        console.log("erreur en récupérant les infos de la ligne dans l'opendata via navitia : " + err)
    }

}

async function send_to_josm(osm_id, ref_to_add){
    try {
        var josm_url = JOSM_url_base + "n" + osm_id
        if (ref_to_add){
            josm_url += '&addtags=ref:FR:STIF=' + ref_to_add;
        }
        var josm_response = await fetch(josm_url);
    } catch (err) {
        alert("Erreur au chargement dans JOSM (avez-vous lancé JOSM et activé le contrôle à distance ?)")
        console.error(err)
    }

}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.href);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
