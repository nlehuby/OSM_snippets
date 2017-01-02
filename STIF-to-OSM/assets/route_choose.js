/*
	nlehuby
*/

var osm_line_id = getParameterByName('osm_line_id');
var navitia_line_id = getParameterByName('navitia_line_id');
// var osm_line_id = 6116962;
// var navitia_line_id = 'line:OIF:051051013:13OIF377';

var navitia_route_list = [];
var osm_route_list = [];

$(document).ready(function() {
    //authentification navitia
    $.ajaxSetup( {
           beforeSend: function(xhr) { xhr.setRequestHeader("Authorization", "Basic " + btoa(navitia_api_key + ":" )); }
          });

   get_osm_routes_for_this_line(osm_line_id);
});

function get_osm_routes_for_this_line(osm_relation_line_id){
  // on récupère les relations enfants de la relation ligne : ce sont les parcours
  $.ajax({
      // [out:json][timeout:25]; relation(107352);rel(r);out tags;
      url: 'https://overpass-api.de/api/interpreter?data=[out:json][timeout:25]; relation('+ osm_relation_line_id +');rel(r);out tags;',
      dataType: 'json',
      global: true,
      error: function(data) {console.log(data)},
      success: function(data) {
          for (i = 0; i < data['elements'].length; i++) {
            relation_data = data['elements'][i]
            osm_route_list.push(relation_data)
          }
          get_navitia_routes_for_this_line(navitia_line_id)
      }
  });
}

function get_navitia_routes_for_this_line(navitia_line_id){
    //on récupère les parcours de la ligne navitia
   $.ajax({
        url: "https://api.navitia.io/v1/coverage/fr-idf/lines/"+ navitia_line_id +"/routes?depth=2",
        dataType: 'json',
        global: true,
        error: function(data) {console.log(data)},
        success: function(data) {
            for (i = 0; i < data['routes'].length; i++) {
                var route_content = {}
                route_content['id'] = data['routes'][i]['id'];
                route_content['name'] = data['routes'][i]['line']['commercial_mode']['name'] + " " + data['routes'][i]['line']['code'] ;
                route_content['name'] += " : " + data['routes'][i]['name'] + "  "
                navitia_route_list.push(route_content)
            }
            display_info();
        }
    });
}

function display_info(){
    var listings = document.getElementById('osm_route_list');

    for (i = 0; i < osm_route_list.length; i++) {
        console.log(osm_route_list[i])
        var osm_route = listings.appendChild(document.createElement('div'));
        var osm_route_name = osm_route.appendChild(document.createElement('h3'));
        osm_route_name.innerHTML = "OSM : ";
        osm_route_name.innerHTML += osm_route_list[i]['tags']['name'] || "<i>Pas de nom</i>";

        for (j = 0; j < navitia_route_list.length; j++) {
            console.log(navitia_route_list[j])
            var link = osm_route.appendChild(document.createElement('p'));
            var redirect = link.appendChild(document.createElement('a'));
            redirect.href="https://parcours-bus.5apps.com/bus_route.htm?osm="+osm_route_list[i]['id']+"&navitia=" +navitia_route_list[j]['id']
            redirect.text=" Rattacher des arrêts"
            redirect.className="button alt small"
            var redirect = link.appendChild(document.createElement('a'));
            redirect.href="./stops_by_route.html?osm_route_id="+osm_route_list[i]['id']+"&navitia_route_id=" +navitia_route_list[j]['id']
            redirect.text=" Ajouter des ref STIF"
            redirect.className="button small"
            var opendata_route_name = link.appendChild(document.createElement('span'));
            opendata_route_name.innerHTML = " >> opendata : " + navitia_route_list[j]['name'];
        }
    }
}

function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.href);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
