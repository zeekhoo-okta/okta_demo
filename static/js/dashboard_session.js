// get csrf token from cookies
var csrftoken = getCookie('csrftoken');
console.log('csrftoken = ' + csrftoken)

// GET sessions/me
var xhttp = new XMLHttpRequest();
xhttp.open("GET", "https://zeekhoo.okta.com/api/v1/sessions/me");
xhttp.withCredentials = true;
xhttp.send();
xhttp.onreadystatechange = function() {
    if (document.readyState == 'complete') {
        var response = xhttp.responseText;
        var status = xhttp.status;
        console.log('sessions/me status=' + status);
        console.log(response);
        // if there is a session, post session info back to the backend
        if (status == 200 && response != null && response != '') {
            session = JSON.parse(response);
            console.log('session:   ' + session.id);
            console.log('userId: ' + session.userId);
            console.log('user: ' + session.login);

            set_session(session.id, session.userId, session.login);
        } else if (status != 0) {
            setMessage();
        }
    }
}

function setMessage() {
    element = document.getElementById('please_message');
    element.innerHTML = 'Please Log In';
}

function set_session(id, userId, login) {
	console.log('Set Django Session and redirect to dashboard');
	xhttp.open("POST", "/session/");
	xhttp.setRequestHeader('X-CSRFToken', csrftoken);
	xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	xhttp.send(JSON.stringify({"id": id, "userId": userId, "user": login}));
    xhttp.onreadystatechange = function() {
	    window.location.href = '/';
	}
}
