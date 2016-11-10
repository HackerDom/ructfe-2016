/*! js-cookie v2.1.3 | MIT */
!function(a){var b=!1;if("function"==typeof define&&define.amd&&(define(a),b=!0),"object"==typeof exports&&(module.exports=a(),b=!0),!b){var c=window.Cookies,d=window.Cookies=a();d.noConflict=function(){return window.Cookies=c,d}}}(function(){function a(){for(var a=0,b={};a<arguments.length;a++){var c=arguments[a];for(var d in c)b[d]=c[d]}return b}function b(c){function d(b,e,f){var g;if("undefined"!=typeof document){if(arguments.length>1){if(f=a({path:"/"},d.defaults,f),"number"==typeof f.expires){var h=new Date;h.setMilliseconds(h.getMilliseconds()+864e5*f.expires),f.expires=h}try{g=JSON.stringify(e),/^[\{\[]/.test(g)&&(e=g)}catch(i){}return e=c.write?c.write(e,b):encodeURIComponent(e+"").replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g,decodeURIComponent),b=encodeURIComponent(b+""),b=b.replace(/%(23|24|26|2B|5E|60|7C)/g,decodeURIComponent),b=b.replace(/[\(\)]/g,escape),document.cookie=b+"="+e+(f.expires?"; expires="+f.expires.toUTCString():"")+(f.path?"; path="+f.path:"")+(f.domain?"; domain="+f.domain:"")+(f.secure?"; secure":"")}b||(g={});for(var j=document.cookie?document.cookie.split("; "):[],k=/(%[0-9A-Z]{2})+/g,l=0;l<j.length;l++){var m=j[l].split("="),n=m.slice(1).join("=");'"'===n.charAt(0)&&(n=n.slice(1,-1));try{var o=m[0].replace(k,decodeURIComponent);if(n=c.read?c.read(n,o):c(n,o)||n.replace(k,decodeURIComponent),this.json)try{n=JSON.parse(n)}catch(i){}if(b===o){g=n;break}b||(g[o]=n)}catch(i){}}return g}}return d.set=d,d.get=function(a){return d.call(d,a)},d.getJSON=function(){return d.apply({json:!0},[].slice.call(arguments))},d.defaults={},d.remove=function(b,c){d(b,"",a(c,{expires:-1}))},d.withConverter=b,d}return b(function(){})});

function CheckLoginState() {
	var login = Cookies.get('name');
	$("#user").text(login || "");
	var $loginBtns = $("#loginBtn");
	var $logoutBtn = $("#logoutBtn");
	if(!login) {
		$loginBtns.show();
		$logoutBtn.hide();
	} else {
		$loginBtns.hide();
		$logoutBtn.show();
	}
}

CheckLoginState();

function OnError($form, error) {
	$form.find(".alert").text(error).stop().show(200).delay(1000).hide(200);
}

function ParseSkills(skills) {
	if (typeof skills === 'undefined')
		return undefined;

	return skills.split(',').map(function(str) { return str.trim(); }).filter(function (skill) { return skill !== ''; });
}

function OnLogin() {
	var $form = $('#login');
	var user = $form.find('[name="user"]').val();
	var password = $form.find('[name="password"]').val();
	var skills = $form.find('[name="skills"]').val();

	var skillsList = ParseSkills(skills);

	$.ajax('/login', {
		type: 'POST',
		data: {'user': user, 'password': password, 'skills': JSON.stringify(skillsList)},
	})
	.always(function(data) {
		console.log(data);
	})
	.done(function() {
		$('#loginModal').modal('hide');
		CheckLoginState();
		myListener.restart();
	})
	.fail(function(xhr) {
		OnError($form, xhr.responseText || xhr.statusMessage || "Unknown error");
	});

	return false;
}

function OnLogout() {
	$.ajax('/logout', {
		type: 'POST'
	})
	.always(function(data) {
		console.log(data);
	})
	.done(CheckLoginState);

	return false;
}

function OnPublish() {
	var $form = $('#publish');
	var title = $form.find('[name="title"]').val();
	var body = $form.find('[name="body"]').val();
	var requirements = $form.find('[name="requirement"]').val()
	var is_public = $form.find('[name="is_public"]').prop('checked') ? 'on' : '';

	$.ajax('/publish', {
		type: 'POST',
		data: {'title': title, 'body': body, 'requirement': requirements, 'is_public': is_public},
	})
	.always(function(data) {
		console.log(data);
	})
	.done(function() {
		$form.find("input[type=text], textarea").val("");
		$form.find('[type=checkbox]').prop('checked', false);
		$('#uploadModal').modal('hide');
	})
	.fail(function(xhr) {
		OnError($form, xhr.responseText || xhr.statusMessage || "Unknown error");
	});

	return false;
}

function LoadPublics() {
	new Listener('publics');
}

function LoadMy() {
	myListener = new Listener('my');
}

$("#login").submit(OnLogin);
$("#logoutBtn").click(OnLogout);
$("#publish").submit(OnPublish);

var myListener;
LoadMy();
LoadPublics();
