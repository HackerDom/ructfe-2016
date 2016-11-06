var Viz = function(infoData, startScoreboard) {
	var LOAD_DATA_INTERVAL = 10*1000;
	var EVENTS_VISUALIZATION_INTERVAL = 1000;
	var COLOR_CONSTANTS = ["#ED953A", "#E5BD1F", "#3FE1D6", "#568AFF", "#8C41DA", "#BA329E"];
	var RED_COLOR = "#EC2B34";
	var DOWN_SERVICE_COLOR = "#1D3542";
	var WIDTH = 1366; // Это базовый размер экрана.
	var HEIGHT = 662;
	var ISLAND_WIDTH = 60;
	var SERVICES_COUNT = 6; // Существующее количество серисов, менять нелья, т.к. шестиугольники.

	var svgWrapperId = "svg-wrapper";
	var svgId = "svg-viz";
	var tooltipContentWrapperClass = "team-tooltip";
	var NOT_STARTED = "0";
	var PLAYING = "1";
	var SUSPEND = "2";
	var FINISHED = "3";
	var timeForArrowAnimation = 0.8;
	var tracePortion = 0.4;
	var whitePortion = 0.1;

	var info = infoData;
	var scoreboard = startScoreboard;
	var teams = [];
	var teamIdToNum = {};
	var services = [];
	var serviceIdToNum = {};
	var nodes;
	var lastGradientId = 0;
	var lastArrowId = 0;
	var openedTooltipTeamId = undefined;

    var cur_round = -1;
    var prev_interval = -1;
    var pending_events = [];

	(function() {
		for (var fieldName in info.teams) {
			if (info.teams.hasOwnProperty(fieldName)) {
				var id = teams.length;
				teams.push({index: id, id: id, team_id: fieldName, name: info.teams[fieldName], score: 0, place: null, status: 0});
				teamIdToNum[fieldName] = teams.length - 1;
			}
		}
	})();
	(function() {
		for (var fieldName in info.services) {
			if (info.services.hasOwnProperty(fieldName)) {
				var id = services.length;
				services.push({id: id, service_id: fieldName, name: info.services[fieldName], color: COLOR_CONSTANTS[id], visible: true});
				serviceIdToNum[fieldName] = services.length - 1;
			}
		}
	})();
	createFilterPanel();
	updateScore();

	var svg = d3.select("#" + svgId);
	var container = svg.append("g").classed("container", true);
	var defs = svg.append("defs");

	var zoom = d3.behavior.zoom().scaleExtent([0.25, 3]).size([WIDTH, HEIGHT]).on("zoom", function () {
		container.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
	});
	svg.call(zoom);

	drawTeams();

	setTimeout(function () {
		events_visualization_loop();
		setInterval(events_visualization_loop, EVENTS_VISUALIZATION_INTERVAL);
	}, 0);

	setTimeout(function () {
		load_data();
		setInterval(load_data, LOAD_DATA_INTERVAL);
	}, 0);


	function load_data() {
		$.getJSON("./scoreboard").done(function (scoreboardData) {
			scoreboard = scoreboardData;
			load_events();
			load_services_statuses();
			updateScore();
			draw_services_statuses();
		});
	}

	// Если начался новый раунд, запрашивает данные за предыдущий и кладет события в pending_events
	// При открытии для предыдущего раунда запрашивает данные сразу.
    function load_events() {
		if (cur_round < 0) { cur_round = scoreboard.round - 1; }
		if (cur_round === scoreboard.round) { return; }
		var next_round = scoreboard.round;

		$.getJSON('./events?from=' + cur_round).done(function (eventsData) {
			for (var i = 0; i < eventsData.length; ++i) {
				if (cur_round <= eventsData[i][0] && eventsData[i][0] < next_round) {
					pending_events.push(eventsData[i]);
				}
			}
			cur_round = next_round;
		});
    }

    function load_services_statuses() {
		// TODO загруэить данные о состояниях сервисов.
		for (var i=0; i<teams.length; i++) {
			teams[i].servicesStatuses = [];
			for (var j = 0; j < services.length; j++) {
				teams[i].servicesStatuses.push(randomInteger(0, 1));
			}
		}
	}

	function draw_services_statuses() {
		d3.selectAll(".node").each(function () {
			var n = d3.select(this);
			var nData = n.data()[0];
			for (var i=0; i<services.length; i++) {
				var isUp = nData.servicesStatuses[i] === 1;
				n.select(".service_" + i).attr("fill", isUp ? services[i].color : DOWN_SERVICE_COLOR);
			}
		});
	}

	function events_visualization_loop() {
		if (scoreboard.status == NOT_STARTED)
			return;

		if (prev_interval < 0) {
			if (pending_events.length > 0)
				prev_interval = pending_events[0][1] - EVENTS_VISUALIZATION_INTERVAL;
			else
				return;
		}

		var prev_interval_end = prev_interval + EVENTS_VISUALIZATION_INTERVAL;
		while (pending_events.length > 0 && pending_events[0][1] < prev_interval_end) {
			var event = pending_events.shift();
			var showArrowFunc = (function (arrowData) {
					return function() { showArrow(arrowData); }
				})({
					from: teamIdToNum[event[3]],
					to: teamIdToNum[event[4]],
					svc: serviceIdToNum[event[2]]
				});
			setTimeout(showArrowFunc, event[1] - prev_interval);
		}
		prev_interval = prev_interval_end;
	}

	function updateScore() {
		var i, j;
		for (i = 0; i < teams.length; i++) {
			teams[i].score = scoreboard.table[teams[i].team_id];
		}
		setPlaces();
		updateOpenedTooltip();
	}

	function setPlaces() {
		var groupsHash = _.groupBy(teams, 'score');
		groupsArray = [];
		for (var groupKey in groupsHash) {
			if (groupsHash.hasOwnProperty(groupKey)) {
				groupsArray.push({'key': parseFloat(groupKey), 'value': groupsHash[groupKey]})
			}
		}
		groupsArray = _.sortBy(groupsArray, 'key').reverse();
		var minPlace = 1;
		for (i = 0; i < groupsArray.length; i++) {
			var teamsInGroup = groupsArray[i].value;
			var maxPlace = minPlace + teamsInGroup.length - 1;
			for (j = 0; j < teamsInGroup.length; j++) {
				if (minPlace === maxPlace)
					teamsInGroup[j].place = minPlace + "";
				else
					teamsInGroup[j].place = minPlace + "-" + maxPlace;
			}
			minPlace = maxPlace + 1;
		}
	}

	function updateOpenedTooltip() {
		if (openedTooltipTeamId == undefined)
			return;
		var team = teams[openedTooltipTeamId];
		var html = createTooltipHtml(team);
		$("." + tooltipContentWrapperClass).empty().append(html);
	}

	function setOptimalZoom() {
		var $svg = $("#" + svgId);
		var realHeight = $svg.height();
		var realWidth = $svg.width();
		var cad = getCetnerAndDelta(teams);
		var size = Math.max(teams[0].width, teams[0].height);
		cad.dx += size * 2;
		cad.dy += size * 2;
		cad.x += size * 0.5;
		cad.y += size * 0.5;
		var scale = Math.min(realWidth / cad.dx, realHeight / cad.dy);
		var translate = [realWidth / 2 - scale * cad.x, realHeight / 2 - scale * cad.y];
		zoom.translate(translate).scale(scale).event(svg);
	}

	function getCetnerAndDelta(nodes) {
		var miny, maxy;
		var minx = miny = Number.MAX_VALUE;
		var maxx = maxy = Number.MIN_VALUE;
		nodes.forEach(function(d) {
			if(d == undefined)
				return;
			minx = Math.min(d.x, minx);
			maxx = Math.max(d.x, maxx);
			miny = Math.min(d.y, miny);
			maxy = Math.max(d.y, maxy);
		});
		var dx = maxx - minx;
		var dy = maxy - miny;
		var x = (maxx + minx ) / 2;
		var y = (maxy + miny) / 2;
		return { x: x, y: y, dx: dx, dy: dy };
	}

	function showArrow(arrow) {
		var service = services[arrow.svc];
		if (!service.visible)
			return;

		var links = container.selectAll(".arrow" + lastArrowId)
			.data([arrow])
			.enter()
			.append("g")
			.attr("class", ".arrow" + lastArrowId);
		lastArrowId++;

		links.each(function () {
			var link = d3.select(this);
			var linkData = link.data()[0];
			var teamFrom = teams[linkData.from];
			var teamTo = teams[linkData.to];
			var fromX = teamFrom.x + teamFrom.width / 2;
			var fromY = teamFrom.y + teamFrom.height / 2;
			var toX = teamTo.x + teamTo.width / 2;
			var toY = teamTo.y + teamTo.height / 2;
			var dx = toX - fromX;
			var dy = toY - fromY;
			var length = Math.sqrt(dx * dx + dy * dy);
			var angleRad = Math.atan2(dy, dx);
			var angle = angleRad * 180 / Math.PI;
			var gradientId = "grad" + lastGradientId;
			var color = service.color;
			lastGradientId++;
			var lineFunction = d3.svg.line()
				.x(function(d) { return d.x; })
				.y(function(d) { return d.y; })
				.interpolate("basis");
			var vec_length = - length / 4; // Вектор из центра линии до кончика параболы.
			var vec_x = vec_length * Math.sin(angleRad); // Изначальный ветор меняется только по y вверх.
			var vec_y = vec_length * Math.cos(angleRad);
			var lineData = [ { "x": fromX, "y": fromY}, { "x": fromX + length / 2 + vec_x, "y": fromY + vec_y}, { "x": fromX + length,  "y": fromY + 0.01} ];
			link.append("path")
				.attr("class", "arrow-line")
				.attr("d", lineFunction(lineData))
				.attr("stroke", "url(#" + gradientId + ")");
			link.attr("transform", "rotate(" + angle + " " + fromX + " " + fromY + ")");
			addGradient(gradientId, color);
			setTimeout(function () {
				link.remove();
				defs.select("#" + gradientId).remove();
			}, timeForArrowAnimation * 1000 * (1 + tracePortion + whitePortion));
			setTimeout(function () {
				addRadialGradient(gradientId + "radial", color);
				var explosion = container.append("circle")
					.attr("class", "explosion")
					.attr("r", teamTo.width / 3)
					.attr("cx", toX)
					.attr("cy", toY)
					.attr("fill", "url(#" + gradientId + "radial" + ")");
				setTimeout(function () {
					explosion.style("fill-opacity", 0);
				}, 100);
				setTimeout(function () {
					defs.select("#" + gradientId + "radial").remove();
					explosion.remove();
				}, timeForArrowAnimation * 1000 * (tracePortion + whitePortion) )
			}, timeForArrowAnimation * 1000);
		});
	}

	function drawTeams() {
		var coordsForTeams = getCoordsForTeams(teams.length);

		nodes = container.selectAll(".node")
			.data(teams)
			.enter()
			.append("g")
			.attr("class", "node");

		nodes.each(function () {
			var node = d3.select(this);
			var nodeData = node.data()[0];
			nodeData.width = ISLAND_WIDTH;
			nodeData.height = ISLAND_WIDTH * 0.866; // sqrt(3)/2
			var coords = coordsForTeams.shift();
			nodeData.x = coords.x;
			nodeData.y = coords.y;
			var poly =
			   [{"x": nodeData.width / 4 , "y": 0},
				{"x": nodeData.width * 3 / 4, "y": 0},
				{"x": nodeData.width, "y": nodeData.height / 2},
				{"x": nodeData.width * 3 / 4, "y": nodeData.height},
				{"x": nodeData.width / 4 , "y": nodeData.height},
				{"x": 0, "y": nodeData.height / 2}];
			node.append("polygon")
				.classed("island", true)
				.attr("points", poly.map(function(d) { return [d.x, d.y].join(",");	}).join(" "))
				.attr("transform", "translate(" + nodeData.x + ", " + nodeData.y + ")");

			var center = {"x": nodeData.width / 2, "y": nodeData.height / 2};
			var shift = 0.55;
			for (var i=0; i<SERVICES_COUNT; i++) {
				var cx = center.x + (center.x - poly[i].x) * shift;
				var cy = center.y + (center.y - poly[i].y) * shift;
				node.append("circle")
					.classed("service", true)
					.classed("service_" + services[i].id, true)
					.attr("r", ISLAND_WIDTH / 12)
					.attr("cx", cx)
					.attr("cy", cy)
					.attr("fill", DOWN_SERVICE_COLOR)
					.attr("transform", "translate(" + nodeData.x + ", " + nodeData.y + ")");
			}
		});

		setOptimalZoom();
	}

	function getCoordsForTeams(count) {
		var nodeWidth = ISLAND_WIDTH;
		var nodeHeight = ISLAND_WIDTH * 0.866; // sqrt(3)/2
		var coords = [];
		var columnsCount = 10;
		for (var i = 0; i < count; i++) {
			var row = Math.floor(i / columnsCount);
			var column = i % columnsCount;
			var isEvenRow = row % 2 === 0;
			var y = nodeHeight / 2 * row;
			var x = nodeWidth * 1.5 * column + (isEvenRow ? 0 : (nodeWidth * 3 / 4));
			coords.push({"x": x, "y": y});
		}
		return coords;
	}

	function randomInteger(min, max) {
		var rand = min - 0.5 + Math.random() * (max - min + 1);
		rand = Math.round(rand);
		return rand;
	}

	$(window).resize(function () {
		setOptimalZoom();
	});

	$("#" + svgWrapperId).tooltip({
		items: ".node",
		track: true,
		show: { effect: "fadeIn", delay: 100, duration: 80 },
		hide: { effect: "fadeOut", delay: 50, duration: 40 },
		content: function() {
			var node = d3.select(this);
			var nodeData = node.data()[0];
			var html = createTooltipHtml(nodeData);
			openedTooltipTeamId = nodeData.id;
			return "<div class='" + tooltipContentWrapperClass + "'>" + html + "</div>";
		},
		close: function() {
			openedTooltipTeamId = undefined;
		}
	});
	$(".ui-helper-hidden-accessible").remove();

	function createTooltipHtml(nodeData) {
		return "<span><span class='header'>Team name:</span> <span class='value'>" + htmlEncode(nodeData.name) + "</span></span><br/>"
			+ "<span><span class='header'>Place:</span> <span class='value'>" + nodeData.place + "</span></span><br/>"
			+ "<span><span class='header'>Score:</span> <span class='value'>" + nodeData.score + "</span></span>";
	}

	function htmlEncode(value){
		return $('<div/>').text(value).html();
	}

	function createFilterPanel() {
		var deselectionFlag = "deselected";
		var $fc = $("#filters-container");

		for (var i=0; i<services.length; i++) {
			var service = services[i];
			var $filter = $('<div class="filter">' + service.name + '</div>');
			$filter.css("color", service.color);
			$filter.click( function(index) {return function () {
				if ($(this).hasClass(deselectionFlag)) {
					$(this).removeClass(deselectionFlag);
					services[index].visible = true;
				} else {
					$(this).addClass(deselectionFlag);
					services[index].visible = false;
				}
			}
			}(i));
			$fc.append($filter);
		}
	}

	function addRadialGradient(id, color) {
		var gradient = defs.append("radialGradient").attr("id", id);
		gradient.append("stop")
			.attr("offset", 0.02)
			.attr("stop-color", "white")
			.attr("stop-opacity", 1);
		gradient.append("stop")
			.attr("offset", 0.37)
			.attr("stop-color", color)
			.attr("stop-opacity", 1);
		gradient.append("stop")
			.attr("offset", 1)
			.attr("stop-color", color)
			.attr("stop-opacity", 0);
	}

	function addGradient(id, color) {
		var startTime = svg[0][0].getCurrentTime();
		var gradient = defs.append("linearGradient").attr("id", id);
		var traceTime = timeForArrowAnimation * tracePortion;
		var whiteTime = timeForArrowAnimation * whitePortion;
		var allTime = timeForArrowAnimation + traceTime + whiteTime;

		gradient.append("stop")
			.attr("offset", 0)
			.attr("stop-color", "white")
			.attr("stop-opacity", 0);
		var stop2 = gradient.append("stop")
			.attr("offset", 0)
			.attr("stop-color", color)
			.attr("stop-opacity", 1);
		stop2.append("animate")
			.attr("attributeName", "stop-opacity")
			.attr("begin", startTime + whiteTime)
			.attr("dur", traceTime)
			.attr("values", "1;0")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop2.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime + traceTime)
			.attr("dur", timeForArrowAnimation)
			.attr("values", "0;1")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop2.append("animate")
			.attr("attributeName", "stop-opacity")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", "0;1")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop2.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", "1;0")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		var stop3 = gradient.append("stop")
			.attr("offset", 0)
			.attr("stop-color", "white")
			.attr("stop-opacity", 1);
		stop3.append("animate")
			.attr("attributeName", "stop-color")
			.attr("begin", startTime)
			.attr("dur", whiteTime)
			.attr("values", "white;" + color)
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop3.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime + whiteTime)
			.attr("dur", timeForArrowAnimation)
			.attr("values", "0;1")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop3.append("animate")
			.attr("attributeName", "stop-opacity")
			.attr("begin", startTime + timeForArrowAnimation + whiteTime)
			.attr("dur", traceTime)
			.attr("values", "1;0")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop3.append("animate")
			.attr("attributeName", "stop-color")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", color + ";white")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop3.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", "1;0")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop3.append("animate")
			.attr("attributeName", "stop-opacity")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", "0;1")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		var stop4 = gradient.append("stop")
			.attr("offset", 0)
			.attr("stop-color", "white")
			.attr("stop-opacity", 1);
		stop4.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime)
			.attr("dur", timeForArrowAnimation)
			.attr("values", "0;1")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop4.append("animate")
			.attr("attributeName", "stop-color")
			.attr("begin", startTime + timeForArrowAnimation)
			.attr("dur", whiteTime)
			.attr("values", "white;" + color)
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop4.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", "1;0")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop4.append("animate")
			.attr("attributeName", "stop-color")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", color + ";white")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		var stop5 = gradient.append("stop")
			.attr("offset", 0)
			.attr("stop-color", "white")
			.attr("stop-opacity", 0);
		stop5.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime)
			.attr("dur", timeForArrowAnimation)
			.attr("values", "0;1")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		stop5.append("animate")
			.attr("attributeName", "offset")
			.attr("begin", startTime + allTime)
			.attr("dur", "0.001s")
			.attr("values", "1;0")
			.attr("repeatCount", 1)
			.attr("fill", "freeze");
		gradient.append("stop")
			.attr("offset", 1)
			.attr("stop-color", "white")
			.attr("stop-opacity", 0);
	}

	return {
		getTeamsData: function() { return teams; },
		getInfo: function() { return info; },
		getScoreboard: function() { return scoreboard; },
		getPendingEvents: function() { return pending_events; }
	}
};
