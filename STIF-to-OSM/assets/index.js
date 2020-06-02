/*
	nlehuby
*/

var table;
//datatables
$(document).ready(function() {
    function parseData(url, callBack) {
        Papa.parse(url, {
            download: true,
            dynamicTyping: true,
            complete: function(results) {
                callBack(results.data);
            }
        });
    }

    parseData("https://raw.githubusercontent.com/Jungle-Bus/ref-fr-STIF/gh-pages/data/lignes.csv", display_lines_in_table);


    function display_lines_in_table(data_lines) {
        data_lines.splice(0, 1);
        data_lines.splice(-1, 1);
        var mapping_needed = 0;
        for (i=0; i<data_lines.length; i++){
            if (!data_lines[i][8]){
                mapping_needed += 1;
            }
        }
        $('#statistics').html("Il reste encore " + mapping_needed + " lignes sur " + data_lines.length + " à associer.");

        table = $('#data_table').DataTable({
            data: data_lines,
            order: [
                [8  , 'asc'],
                [1  , 'desc']
            ],
            columns: [
                //line_id,code,name,network,operator,colour,osm:type,mode,osm:ref:FR:STIF:ExternalCode_Line
                {
                    title: "id",
                    searchable: false ,
                    data: function(row, type, set) {
                        var osm_id = row[0].split(':')[2]
                        var link_url = "https://jungle-bus.github.io/unroll/route.html?line=" + osm_id;
                        return "<a target='_blank' href='" + link_url + "'>" + osm_id + "</a>";
                    }
                }, {
                    title: "code",
                    data: function(row, type, set) {
                        return `
                        <transport-thumbnail
                            data-transport-mode="${row['7']}"
                            data-transport-line-code="${row['1']}"
                            data-transport-line-color="${row['5']}">
                        </transport-thumbnail>
                        `
                    }
                }, {
                    title: "nom"
                }, {
                    title: "réseau"
                }, {
                    title: "opérateur"
                }, {
                    title: "colour",
                    visible:false
                }, {
                    title: "type",
                    visible: false
                }, {
                    title: "mode"
                }, {
                    title: "code STIF"
                }, {
                    title: "Associer",
                    data: function(row, type, set) {
                        if (row[8] != "") {
                            button_color = "special";
                            navitia_url_suffix = "";
                        } else {
                            button_color = "";
                            navitia_url_suffix = "&line_code=" + row[1];
                        }
                        return "<a class='button " + button_color + " small' target='_blank' href='./line.html?osm_relation=" + row[0].split(':')[2] + navitia_url_suffix + "'> Voir </a>";
                    }
                }
            ]
        });
    }
});





//connexion Oauth
document.getElementById('OSM_authenticate').onclick = function() {
    auth.authenticate(function() {
        console.log("authenfication terminée")
        update_auth_visual_return()
    });
};
document.getElementById('OSM_logout').onclick = function() {
    auth.logout();
    console.log("déconnexion en cours");
    update_auth_visual_return()
};

update_auth_visual_return();

//affichage du login OSM si connecté
function show_OSM_username() {
    auth.xhr({
        method: 'GET',
        path: '/api/0.6/user/details'
    }, OSM_user_name_done);
}

function OSM_user_name_done(err, res) {
    if (err) {
        console.log(err);
        alert("Échec autour de l'authentification OSM")
        return;
    }
    var u = res.getElementsByTagName('user')[0];
    document.getElementById('OSM_user').innerHTML = u.getAttribute('display_name');

}

function update_auth_visual_return() {
    //affichage des bandeaux d'avertissement
    if (auth.authenticated()) {
        document.getElementById('alert_no_auth').style.display = 'none';
        document.getElementById('OSM_authenticate').style.display = 'none';
        document.getElementById('alert_auth').style.display = 'block';
        show_OSM_username();
    } else {
        document.getElementById('alert_auth').style.display = 'none';
        document.getElementById('alert_no_auth').style.display = 'block';
        document.getElementById('OSM_authenticate').style.display = 'block';
    }
}
