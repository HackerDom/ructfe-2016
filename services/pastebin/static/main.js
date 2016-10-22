function GetCredentials($form) {
	var user = $form.children('[name="user"]').val();
	var password = $form.children('[name="password"]').val();

	return {'user': user, 'password': password};
}

function OnPost(id) {
	var $form = $('#' + id);
	var credentials = GetCredentials($form);

	$.ajax('/' + id,
	{
		type: 'POST',
		data: credentials
	})
	.always(function(data) {
		console.log(data);
	})

	return false;
}

function OnRegister() {
	return OnPost('register');
}

function OnLogin() {
	return OnPost('login');
}

function OnLogout() {
	$.ajax('/logout', 
	{
		type: 'GET'
	})
	.always(function(data) {
		console.log(data);
	});

	return false;
}

function OnUpload() {
	var $form = $('#upload')[0];
	var data = new FormData($form);

	$.ajax('/upload', 
	{
		type: 'POST',
		data: data,
		cache: false,
		contentType: false,
		processData: false
	})
	.always(function(data) {
		console.log(data);
	});

	return false;
}

function OnLoadPublics() {
	var url = 'ws://' + window.location.hostname + ':' + window.location.port + '/publics';
	var socket = new WebSocket(url);

	socket.onopen = function() {
		console.log('opened!!!');
	}
	socket.onmessage = function(event) {
		console.log(event.data);
	}
//	socket.onclose = OnLoadPublics;
}
