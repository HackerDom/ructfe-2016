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

function OnPublish() {
	var $form = $('#publish');
	var title = $form.children('[name="title"]').val();
	var body = $form.children('[name="body"]').val();	
	var is_public = $form.children('[name="is_public"]').prop('checked') ? 'on' : '';

	$.ajax('/publish', 
	{
		type: 'POST',
		data: {'title': title, 'body': body, 'is_public': is_public},
	})
	.always(function(data) {
		console.log(data);
	});

	return false;
}

function TTLToString(time) {
	var sec = time % 60;
	var min = Math.floor(time / 60);
	return ('0' + min).slice(-2) + ':' + ('0' + sec).slice(-2);
}

function OnLoadPublics() {
	var url = 'ws://' + window.location.hostname + ':' + window.location.port + '/publics';
	var table = $('#publics');
	var socket = new WebSocket(url);

	socket.onmessage = function(event) {
		console.log(event.data);
		var data = JSON.parse(event.data);
		var owner = $('<td></td>').text(data.owner);
		var link = $('<a></a>').text(data.title);
		link.attr('href', data.url);
		link = $('<td></td>').append(link);
		var ttl = $('<td></td>').text(TTLToString(data.ttl));
		var tr = $('<tr></tr>').append(link, ttl, owner);
		table.append(tr);
	}
	socket.onclose = OnLoadPublics;
}
