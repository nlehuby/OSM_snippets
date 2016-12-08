/*
	nlehuby
*/


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

function update_auth_visual_return(){
    //affichage des bandeaux d'avertissement
    if (auth.authenticated())
    {
        document.getElementById('alert_no_auth').style.display = 'none';
        document.getElementById('OSM_authenticate').style.display = 'none';
        document.getElementById('alert_auth').style.display = 'block';
        show_OSM_username();
    }
    else
    {
        document.getElementById('alert_auth').style.display = 'none';
        document.getElementById('alert_no_auth').style.display = 'block';
        document.getElementById('OSM_authenticate').style.display = 'block';
    }
}
