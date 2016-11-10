/*! ReconnectingWebSocket 1.0.1 | https://github.com/joewalnes/reconnecting-websocket | (c) Joe Walnes | MIT license */
(function(a,c){"function"===typeof define&&define.amd?define([],c):"undefined"!==typeof module&&module.exports?module.exports=c():a.ReconnectingWebSocket=c()})(this,function(){function a(c,q,h){function g(b,a){var d=document.createEvent("CustomEvent");d.initCustomEvent(b,!1,!1,a);return d}var n={debug:!1,automaticOpen:!0,reconnectInterval:1E3,maxReconnectInterval:3E4,reconnectDecay:1.5,timeoutInterval:2E3,maxReconnectAttempts:null,binaryType:"blob"};h||(h={});for(var l in n)this[l]="undefined"!==typeof h[l]?h[l]:n[l];this.url=c;this.reconnectAttempts=0;this.readyState=WebSocket.CONNECTING;this.protocol=null;var b=this,e,p=!1,m=!1,d=document.createElement("div");d.addEventListener("open",function(a){b.onopen(a)});d.addEventListener("close",function(a){b.onclose(a)});d.addEventListener("connecting",function(a){b.onconnecting(a)});d.addEventListener("message",function(a){b.onmessage(a)});d.addEventListener("error",function(a){b.onerror(a)});this.addEventListener=d.addEventListener.bind(d);this.removeEventListener=d.removeEventListener.bind(d);this.dispatchEvent=d.dispatchEvent.bind(d);this.open=function(k){e=new WebSocket(b.url,q||[]);e.binaryType=this.binaryType;if(k){if(this.maxReconnectAttempts&&this.reconnectAttempts>this.maxReconnectAttempts)return}else d.dispatchEvent(g("connecting")),this.reconnectAttempts=0;(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","attempt-connect",b.url);var c=e,h=setTimeout(function(){(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","connection-timeout",b.url);m=!0;c.close();m=!1},b.timeoutInterval);e.onopen=function(c){clearTimeout(h);(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onopen",b.url);b.protocol=e.protocol;b.readyState=WebSocket.OPEN;b.reconnectAttempts=0;c=g("open");c.isReconnect=k;k=!1;d.dispatchEvent(c)};e.onclose=function(c){clearTimeout(f);e=null;if(p)b.readyState=WebSocket.CLOSED,d.dispatchEvent(g("close"));else{b.readyState=WebSocket.CONNECTING;f=g("connecting");f.code=c.code;f.reason=c.reason;f.wasClean=c.wasClean;d.dispatchEvent(f);k||m||((b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onclose",b.url),d.dispatchEvent(g("close")));var f=b.reconnectInterval*Math.pow(b.reconnectDecay,b.reconnectAttempts);setTimeout(function(){b.reconnectAttempts++;b.open(!0)},f>b.maxReconnectInterval?b.maxReconnectInterval:f)}};e.onmessage=function(c){(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onmessage",b.url,c.data);var e=g("message");e.data=c.data;d.dispatchEvent(e)};e.onerror=function(c){(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","onerror",b.url,c);d.dispatchEvent(g("error"))}};1==this.automaticOpen&&this.open(!1);this.send=function(c){if(e)return(b.debug||a.debugAll)&&console.debug("ReconnectingWebSocket","send",b.url,c),e.send(c);throw"INVALID_STATE_ERR : Pausing to reconnect websocket";};this.close=function(b,a){"undefined"==typeof b&&(b=1E3);p=!0;e&&e.close(b,a)};this.refresh=function(){e&&e.close()}}if("WebSocket"in window)return a.prototype.onopen=function(a){},a.prototype.onclose=function(a){},a.prototype.onconnecting=function(a){},a.prototype.onmessage=function(a){},a.prototype.onerror=function(a){},a.debugAll=!1,a.CONNECTING=WebSocket.CONNECTING,a.OPEN=WebSocket.OPEN,a.CLOSING=WebSocket.CLOSING,a.CLOSED=WebSocket.CLOSED,a});

function Listener(action) {
	this.restart = function() {
		this.table.empty();
		this.shown.clear();
		this.socket.refresh();
	}

	this.appendPostInfo = function(data) {
		if (this.shown.has(data.url))
			return;
		this.shown.add(data.url);
		var owner = $('<td></td>').text('by ' + data.owner);
		var link = $('<td></td>').text(data.title);
		var tr = $('<tr></tr>').append(link, owner);
		tr.data('url', data.url);
		tr.click(OnShowPost);
		this.table.append(tr);
	}

	this.start = function(action) {
		var url = 'ws://' + window.location.hostname + ':' + window.location.port + '/' + action;
		console.log(url);

		var socket = new ReconnectingWebSocket(url);
		socket.timeoutInterval = 5000;
		socket.reconnectInterval = 3000;

		socket.onopen = function() {
			console.log("open");
		};

		socket.onclose = function(event) {
			console.log("error");
		};

		var cl = this;
		socket.onmessage = function(event) {
			console.log(event.data);
			try {
				var data = JSON.parse(event.data);
				cl.appendPostInfo(data)
			} catch(err) {
				console.log(err);
			}
		}

		return socket;
	}

	this.shown = new Set();
	this.socket = this.start(action);
	this.table = $('#' + action);
}

function InitHistory() {
	$('#postModal,#postErrorModal').on('hidden.bs.modal', function() { 
		history.pushState('', '', '/'); 
	});

	window.onpopstate = function(event) {
		var url = event.state;
		if (typeof url === 'undefined' || url === '')
			$('#postModal, #postErrorModal').modal('hide');
		else if (url == null)
			$('#postErrorModal').modal('show');
		else
			ShowPost(url);
	}

	var url = location.search.substring(1).split('&').map(function(param) {return param.split('=');}).filter(function(pair) {return pair[0] === 'url';}).map(function(pair){return pair[1];})[0];
	if (typeof url !== 'undefined')
		ShowPost(url);
}

function ShowPost(url) {
	$.ajax(url, {
		type: 'GET'
	})
	.always(function(data) {
		console.log(data);
	})
	.done(function(data) {
		$('#postTitle').text(data.title);
		$('#postBody').text(data.body);
		$('#postAuthor').text(data.owner);
		var ok = $('#verified');
		if (typeof data.sign !== 'undefined' && data.sign !== '')
			ok.removeClass('hidden');
		else
			ok.addClass('hidden');
		$('#postModal').modal('show');
	})
	.fail(function(data) {
		if (data.status == 404)
			$('#postErrorModal').modal('show');
	});
}

function OnShowPost(event) {
	var tr = $(event.currentTarget);
	var url = tr.data('url');

	history.pushState(url, '', '?url=' + encodeURI(url));

	ShowPost(url);
}

InitHistory();