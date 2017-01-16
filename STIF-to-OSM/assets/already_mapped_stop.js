/*
	nlehuby
*/

var attr_osm = 'Map data &copy; <a href="http://openstreetmap.org/">OpenStreetMap</a> contributors',
attr_overpass = 'stops from <a href="http://www.overpass-api.de/">Overpass API</a> and <a href="http://navitia.io/">navitia.io</a>';
var osm = new L.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {opacity: 0.7, attribution: [attr_osm, attr_overpass].join(', ')});

var map = new L.Map('map').addLayer(osm).setView(new L.LatLng(48.84702,2.37705), 14);
L.control.scale().addTo(map);

var osm_stop_id = getParameterByName('osm_stop_id');
//var osm_stop_id = 472985886; //cas simple
//var osm_stop_id = 928458342; //cas avec plusieurs arrêts opendata

var tag_to_match = "ref:FR:STIF";


$(document).ready(function() {
    //authentification navitia
    $.ajaxSetup( {
           beforeSend: function(xhr) { xhr.setRequestHeader("Authorization", "Basic " + btoa(navitia_api_key + ":" )); }
          });

   get_osm_stop_info(osm_stop_id);

});

function get_navitia_stops_by_ref_id(ref_id){
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/stop_points?filter=stop_point.has_code(ZDEr_ID_REF_A,"+ ref_id+")",
        dataType: 'json',
        global: true,
        error: function(data) {console.log(data);alert("Il y a eu un souci dans l'affichage des données opendata correspondant à cet arrêt")},
        success: function(data) {
            on_navitia_stop(data);
            }
        });
}

function get_navitia_routes_at_this_stop(stop_id, stop_name){
    $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/stop_points/"+stop_id+"/routes?depth=2",
        dataType: 'json',
        global: true,
        error: function(data) {console.log(data);alert("Il y a eu un souci dans l'affichage des données opendata correspondant à cet arrêt")},
        success: function(data) {
            on_navitia_routes_at_stop(data, stop_name);
            }
        });
}

relations_bus = {};
function get_osm_stop_info(stop_id){
  url_op_bus = 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25];(node(' + stop_id + ');)->.a;rel(bn); out body;.a out body;';

  $.getJSON(url_op_bus, function(data) {
      geo = osmtogeojson(data);

      for (i = 0; i < geo.features.length; i++) {
          if (geo.features[i].properties['type'] == 'node') {
              bus_stop_id = geo.features[i].properties['id'];
              bus_stop_content = {};
              bus_stop_content.name = geo.features[i].properties.tags.name || '<i> pas de nom </i>';

              var ref_STIF_brut = geo.features[i].properties.tags[tag_to_match]
              if (!ref_STIF_brut){
                alert("Pas d'association opendata pour cet arrêt !")
              }
              document.getElementById("osm_ref_match").innerHTML = ref_STIF_brut;
              bus_stop_content.ref_STIF = ref_STIF_brut.split(";")
              for (k = 0; k < bus_stop_content.ref_STIF.length; k++) {
                get_navitia_stops_by_ref_id(bus_stop_content.ref_STIF[k])
              }

              //récupération des parcours desservis d'après OSM
              relations_bus[bus_stop_id] = [];
              for (j = 0; j < geo.features[i].properties['relations'].length; j++) {
                  if (geo.features[i].properties['relations'][j]['reltags']['type'] == 'route') {
                      rel_name = '[' + (geo.features[i].properties['relations'][j]['reltags']['network'] || '' ) + '] '
                      rel_name += geo.features[i].properties['relations'][j]['reltags']['ref'] + ' > ' + geo.features[i].properties['relations'][j]['reltags']['to']
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

              geo.features[i].properties['popup_content'] = popup_content;
              document.getElementById("osm_stop_info").innerHTML = popup_content;
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

function on_navitia_stop(whole_navitia_info){
  stop_name = whole_navitia_info['stop_points'][0]['name'];
  stop_id = whole_navitia_info['stop_points'][0]['id'];
  stop_codes = whole_navitia_info['stop_points'][0]['codes'];
  for (j = 0; j < stop_codes.length; j++) {
      if (stop_codes[j]['type'] == "ZDEr_ID_REF_A"){
          stop_ref_opendata = stop_codes[j]['value']
      }
  }
  stop_name += " - ref:FR:STIF : " + stop_ref_opendata;

  get_navitia_routes_at_this_stop(stop_id, stop_name)

  nav_img = L.icon({iconUrl: 'assets/img/black_bus.png', popupAnchor: [0, 0]});
  stop_marker = L.marker([whole_navitia_info['stop_points'][0]['coord']['lat'], whole_navitia_info['stop_points'][0]['coord']['lon']], {icon: nav_img});
  stop_marker.addTo(map).bindPopup('<h3>'+stop_name+'</h3><div><a href="http://canaltp.github.io/navitia-playground/play.html?request=api.navitia.io/v1/coverage/fr-idf/stop_points/' + stop_id + '" target="_blank"> voir le détail</a></div>');

}

function on_navitia_routes_at_stop(whole_navitia_info, stop_name){
  route_id = whole_navitia_info['routes'][0]['id']

  routes_at_stop = []
  for (j = 0; j < whole_navitia_info['routes'].length; j++) {
    var network = whole_navitia_info['routes'][j]['line']['network']['name'];
    var line_code = whole_navitia_info['routes'][j]['line']['code'];
    var line_destination = whole_navitia_info['routes'][j]['direction']['name'];

    var route_name = "[" + network + "] " + line_code + " > " + line_destination;
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
