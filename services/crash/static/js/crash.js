function loadCrashes() {
	$.getJSON('/crashes').done(function (reports_data) {
		if (reports_data.length === 0)
			return;
		var $table = $("#reports-table");
		for (var i=0; i<reports_data.length; i++) {
			var report = reports_data[i];
			var $row = $("<tr></tr>");
			if (report.guid !== undefined) {
				var $guidElem = $("<a href='#'></a>")
					.text(report.guid)
					.attr("href", "/report.html?guid=" + encodeURIComponent(report.guid));
				$row.append($("<td></td>").append($guidElem));
			} else {
				$(".guid").hide();
			}
			$row.append($("<td></td>").text(report.service_name));
			$row.append($("<td></td>").text(report.signature));
			$row.append($("<td></td>").text(report.time));
			$table.append($row);
		}
		$("#sevice-content-wrapper").show();
	});
}

function loadCrash() {
	var guid = getUrlParameter("guid");
	$("#crash_guid").text(guid);
	$.getJSON('/' + encodeURIComponent(guid)).done(function (crash_data) {
		if (crash_data.crash_address == "" && crash_data.crash_reason == "" && crash_data.crash_thread_stack.length == 0)
			return;
		$("#crash_reason").text(crash_data.crash_reason);
		$("#crash_address").text(crash_data.crash_address);
		$("#remote_ip").text(crash_data.remote_ip);
		$("#load-crash").attr("href", "/" + encodeURIComponent(guid) + "/get");
		var $table = $("#crash-thread-stack-table");
		for (var i=0; i<crash_data.crash_thread_stack.length; i++) {
			var record = crash_data.crash_thread_stack[i];
			var $row = $("<tr></tr>")
				.append($("<td></td>").text(record.idx))
				.append($("<td></td>").text(record.module))
				.append($("<td></td>").text(record.signature))
				.append($("<td></td>").text(record.source))
				.append($("<td></td>").text(record.line));
			$table.append($row);
		}
		$("#sevice-content-wrapper").show();
	});
}

function getUrlParameter(sParam) {
	var sPageURL = decodeURIComponent(window.location.search.substring(1)),
		sURLVariables = sPageURL.split('&'),
		sParameterName,
		i;

	for (i = 0; i < sURLVariables.length; i++) {
		sParameterName = sURLVariables[i].split('=');

		if (sParameterName[0] === sParam) {
			return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
		}
	}
};

if(!!$("#reports-table").length) {
	loadCrashes();
}
if(!!$("#report-props-table").length) {
	loadCrash();
}
