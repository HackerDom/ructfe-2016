/*! ReconnectingWebSocket 1.0.1 | https://github.com/joewalnes/reconnecting-websocket | (c) Joe Walnes | MIT license */
(function(a,c){"function"===typeof define&&define.amd?define([],c):"undefined"!==typeof module&&module.exports?module.exports=c():a.ReconnectingWebSocket=c()})(this,function(){function a(c,q,h){function g(b,a){var d=document.createEvent("CustomEvent");d.initCustomEvent(b,!1,!1,a);return d}var n={debug:!1,automaticOpen:!0,reconnectInterval:1E3,maxReconnectInterval:3E4,reconnectDecay:1.5,timeoutInterval:2E3,maxReconnectAttempts:null,binaryType:"blob"};h||(h={});for(var l in n)this[l]="undefined"!==typeof h[l]?h[l]:n[l];this.url=c;this.reconnectAttempts=0;this.readyState=WebSocket.CONNECTING;this.protocol=null;var b=this,e,p=!1,m=!1,d=document.createElement("div");d.addEventListener("open",function(a){b.onopen(a)});d.addEventListener("close",function(a){b.onclose(a)});d.addEventListener("connecting",function(a){b.onconnecting(a)});d.addEventListener("message",function(a){b.onmessage(a)});d.addEventListener("error",function(a){b.onerror(a)});this.addEventListener=d.addEventListener.bind(d);this.removeEventListener=d.removeEventListener.bind(d);this.dispatchEvent=d.dispatchEvent.bind(d);this.open=function(k){e=new WebSocket(b.url,q||[]);e.binaryType=this.binaryType;if(k){if(this.maxReconnectAttempts&&this.reconnectAttempts>this.maxReconnectAttempts)return}else d.dispatchEvent(g("connecting")),this.reconnectAttempts=0;(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",b.url);var c=e,h=setTimeout(function(){(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",b.url);m=!0;c.close();m=!1},b.timeoutInterval);e.onopen=function(c){clearTimeout(h);(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",b.url);b.protocol=e.protocol;b.readyState=WebSocket.OPEN;b.reconnectAttempts=0;c=g("open");c.isReconnect=k;k=!1;d.dispatchEvent(c)};e.onclose=function(c){clearTimeout(f);e=null;if(p)b.readyState=WebSocket.CLOSED,d.dispatchEvent(g("close"));else{b.readyState=WebSocket.CONNECTING;f=g("connecting");f.code=c.code;f.reason=c.reason;f.wasClean=c.wasClean;d.dispatchEvent(f);k||m||((b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",b.url),d.dispatchEvent(g("close")));var f=b.reconnectInterval*Math.pow(b.reconnectDecay,b.reconnectAttempts);setTimeout(function(){b.reconnectAttempts++;b.open(!0)},f>b.maxReconnectInterval?b.maxReconnectInterval:f)}};e.onmessage=function(c){(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",b.url,c.data);var e=g("message");e.data=c.data;d.dispatchEvent(e)};e.onerror=function(c){(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",b.url,c);d.dispatchEvent(g("error"))}};1==this.automaticOpen&&this.open(!1);this.send=function(c){if(e)return(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",b.url,c),e.send(c);throw"INVALID_STATE_ERR : Pausing to reconnect websocket";};this.close=function(b,a){"undefined"==typeof b&&(b=1E3);p=!0;e&&e.close(b,a)};this.refresh=function(){e&&e.close()}}if("WebSocket"in window)return a.prototype.onopen=function(a){},a.prototype.onclose=function(a){},a.prototype.onconnecting=function(a){},a.prototype.onmessage=function(a){},a.prototype.onerror=function(a){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});

function GetCredentials($form) {
	var user = $form.children('[name="user"]').val();
	var password = $form.children('[name="password"]').val();

	return {'user': user, 'password': password};
}

function OnError($form, error) {
	$form.find(".alert").text(error).stop().show(200).delay(1000).hide(200);
}

function OnPost(action) {
	var $form = $('#' + action);
	var credentials = GetCredentials($form);

	$.ajax('/' + action, {
		type: 'POST',
		data: credentials
	})
	.always(function(data) {
		console.log(data);
	})
	.fail(function(xhr) {
		OnError($form, xhr.responseText || xhr.statusMessage || "Unknown error");
	});

	return false;
}

function OnRegister() {
	return OnPost('register');
}

function OnLogin() {
	return OnPost('login');
}

function OnLogout() {
	$.ajax('/logout', {
		type: 'POST'
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

	$.ajax('/publish', {
		type: 'POST',
		data: {'title': title, 'body': body, 'is_public': is_public},
	})
	.always(function(data) {
		console.log(data);
	})
	.fail(function(xhr) {
		OnError($form, xhr.responseText || xhr.statusMessage || "Unknown error");
	});

	return false;
}

function LoadPublics() {
	var url = 'ws://' + window.location.hostname + ':' + window.location.port + '/publics';
	console.log(url);
	var $table = $('#publics');

	var socket = new ReconnectingWebSocket(url);
	socket.timeoutInterval = 5000;
	socket.reconnectInterval = 3000;

	socket.onopen = function() {
		console.log("open");
	};

	socket.onclose = function(event) {
		console.log("error");
	};

	socket.onmessage = function(event) {
		console.log(event.data);
		try {
			var data = JSON.parse(event.data);
			AppendPostInfo($table, data)
		} catch(err) {
			console.log(err);
		}
	}
}

function LoadMy() {
	setInterval(function() {
		var $table = $('#my');
		$.ajax('/all', {
			type: 'GET'
		})
		.done(function(data) {
			$table.empty();
			data.forEach(function(item) {AppendPostInfo($table, item)});
		});
	},
	60000);
}

function AppendPostInfo(table, data) {
	var $owner = $('<td></td>').text(data.owner);
	var $link = $('<a></a>').text(data.title);
	$link.attr('href', data.url);
	$link = $('<td></td>').append($link);
	var $tr = $('<tr></tr>').append($link, $owner);
	table.append($tr);
}

$("#register").submit(OnRegister);
$("#login").submit(OnLogin);
$("#logout").click(OnLogout);
$("#publish").submit(OnPublish);

LoadMy();
LoadPublics();
