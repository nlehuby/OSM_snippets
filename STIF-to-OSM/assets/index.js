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

    parseData("data/lignes.csv", display_lines_in_table);


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
                [8  , 'asc']
            ],
            columns: [ //@id,ref,name,network,operator,colour,type,route_master,ref:FR:STIF:ExternalCode_Line
                {
                    title: "id"
                }, {
                    title: "code"
                }, {
                    title: "nom"
                }, {
                    title: "réseau"
                }, {
                    title: "opérateur"
                }, {
                    title: "colour",
                    visible: false
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
                        button_color = ""
                        if (row[8] != "") {
                            button_color = "alt"
                        }
                        return "<a class='button " + button_color + " small' target='_blank' href='./line.html?osm_relation=" + row[0] + "&line_code=" + row[1] + "'> Voir </a>";
                    }
                }
            ]
        });
    }

    //rendre le bouton utilisable
    $('#data_table tbody').on('click', 'button', function() {
        var data = table.row($(this).parents('tr')).data();
        console.log(data)
        alert(data[0] + "'s salary is: " + data[1]);
    });
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
