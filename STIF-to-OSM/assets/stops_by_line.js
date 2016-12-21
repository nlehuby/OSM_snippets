/*
	nlehuby
*/

var attr_osm = 'Map data &copy; <a href="http://openstreetmap.org/">OpenStreetMap</a> contributors',
attr_overpass = 'stops from <a href="http://www.overpass-api.de/">Overpass API</a> and <a href="http://navitia.io/">navitia.io</a>';
var osm = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {opacity: 0.7, attribution: [attr_osm, attr_overpass].join(', ')});

var map = new L.Map('map').addLayer(osm).setView(new L.LatLng(48.84702,2.37705), 14);

var osm_line_id = getParameterByName('osm_route_id');
var navitia_line_id = getParameterByName('osm_route_id');
var osm_line_id = 6101989; // 107352;
var navitia_line_id = 'line:OIF:052052033:33OIF456';

var tag_to_match = "ref:FR:STIF";

var osm_stop_list = []
var navitia_stop_list = []

$(document).ready(function() {
    //authentification navitia
    $.ajaxSetup( {
           beforeSend: function(xhr) { xhr.setRequestHeader("Authorization", "Basic " + btoa(navitia_api_key + ":" )); }
          });

   get_osm_info_for_this_line(osm_line_id);
});

function get_osm_info_for_this_line(osm_relation_line_id){
  // on récupère les relations enfants de la relation ligne : ce sont les parcours
  $.ajax({
      // [out:json][timeout:25]; relation(107352);rel(r);out tags;
      url: 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; relation('+ osm_relation_line_id +');rel(r);out tags;',
      dataType: 'json',
      global: true,
      error: function(data) {console.log(data)},
      success: function(data) {
          var params_appel = []
          for (i = 0; i < data['elements'].length; i++) {
            relation_data = data['elements'][i]
            if (relation_data['tags']['public_transport:version'] == "2") {
                params_appel.push({'id':relation_data['id'], 'role': 'platform'})
            } else if (relation_data['tags']['public_transport:version'] == "1") {
                params_appel.push({'id':relation_data['id'], 'role': 'stop'})
            } else {
                alert ('tag public_transport:version manquant')
            }
          }
          get_stops_from_osm_routes(params_appel )
      }
  });
}

function get_stops_from_osm_routes(array_with_routes_and_roles){
  // on reconstruit un appel overpass pour récupérer tous les arrêts des parcours, avec les rôles qu'on a déterminé précédemment

  //[out:json][timeout:25]; (relation(1103949);node(r:"stop");)->.a;rel(bn);out body;.a out body; (relation(1103948);node(r:"stop");)->.a;rel(bn);out body;.a out body;
  var url_overpass = "https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; ";
  for (i = 0; i < array_with_routes_and_roles.length; i++) {
    url_overpass += '(relation('+array_with_routes_and_roles[i]['id']+');node(r:"'+array_with_routes_and_roles[i]['role'] +'");)->.a;rel(bn);out body;.a out body;'
  }

  $.getJSON(url_overpass, function(data) {
      geo = osmtogeojson(data);
      console.log(geo)
      for (i = 0; i < geo.features.length; i++) {
          if (geo.features[i].properties['type'] == 'node') {
              var stop_content = {}
              stop_content['id'] = geo.features[i].properties['id'];
              stop_content['name'] = geo.features[i].properties.tags.name || '<i> pas de nom </i>';
              stop_content['ref'] =  geo.features[i].properties.tags[tag_to_match]
              stop_content['lat'] = geo.features[i]['geometry']['coordinates'][1]
              stop_content['lon'] = geo.features[i]['geometry']['coordinates'][0]

              //récupération des parcours desservis d'après OSM
              stop_content['relations'] = "";
              for (j = 0; j < geo.features[i].properties['relations'].length; j++) {
                  if (geo.features[i].properties['relations'][j]['reltags']['type'] == 'route') {
                      rel_name = '[' + (geo.features[i].properties['relations'][j]['reltags']['network'] || '' ) + '] '
                      rel_name += geo.features[i].properties['relations'][j]['reltags']['ref'] + ' > ' + geo.features[i].properties['relations'][j]['reltags']['to']
                      rel_name += '<br/>'
                      stop_content['relations'] += rel_name
                  }
              }
              osm_stop_list.push(stop_content)
          }
      }

      console.log(osm_stop_list)
      //maintenant qu'on a les arrêts OSM, on récupère les arrêts navitia

      get_stops_from_navitia_line(navitia_line_id)
  });

}

function get_stops_from_navitia_line(navitia_line_id){
    //on récupère tous les arrêts de la ligne navitia
   $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/lines/"+ navitia_line_id +"/stop_points?count=500",
        dataType: 'json',
        global: true,
        error: function(data) {console.log(data)},
        success: function(data) {

            for (i = 0; i < data['stop_points'].length; i++) {
                var stop_content = {}
                stop_content['id'] = data['stop_points'][i]['id'];
                stop_content['name'] = data['stop_points'][i]['name'];
                stop_content['ref'] =  ""
                for (j = 0; j < data['stop_points'][i]['codes'].length; j++) {
                    if (data['stop_points'][i]['codes'][j]['type'] == "ZDEr_ID_REF_A"){
                        stop_content['ref'] = data['stop_points'][i]['codes'][j]['value']
                    }
                }
                stop_content['lat'] = data['stop_points'][i]['coord']['lat']
                stop_content['lon'] = data['stop_points'][i]['coord']['lon']
                navitia_stop_list.push(stop_content)
            }
          console.log(navitia_stop_list)
          // on a maintenant le nécessaire pour commencer à mapper :)
        }
    });
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.href);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
