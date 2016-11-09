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

	var allCoords = [[855,545],[855,493],[810,519],[810,571],[855,597],[900,571],[945,545],[990,571],[945,597],[900,623],[945,649],[990,675],[945,701],[900,675],[270,311],[270,363],[315,337],[360,363],[405,337],[360,311],[360,259],[315,285],[315,389],[360,415],[315,441],[360,467],[405,441],[405,389],[450,415],[450,467],[405,493],[315,493],[360,519],[405,545],[450,519],[495,493],[540,467],[540,415],[495,441],[495,389],[360,623],[360,675],[360,571],[405,597],[990,519],[1035,545],[990,467],[945,441],[1035,493],[1080,519],[1125,493],[1080,467],[1125,441],[1080,415],[1035,441],[1035,389],[990,415],[945,389],[900,363],[945,337],[990,363],[1125,545],[1170,571],[1215,597],[1260,623],[1305,649],[1350,623],[1305,597],[1260,571],[1215,545],[1170,519],[1215,493],[1170,467],[1170,415],[1215,441],[585,649],[585,701],[585,753],[630,727],[675,753],[675,701],[630,675],[540,727],[495,753],[585,857],[585,805],[630,883],[630,831],[630,779],[675,805],[720,831],[765,805],[810,831],[810,883],[765,857],[720,883],[765,909],[675,857],[540,883],[585,909],[540,831],[495,857],[450,883],[1260,467],[1305,441],[1350,467],[1305,493],[1260,519],[1305,545],[1080,571],[270,259],[225,285],[225,337],[225,389],[180,363],[135,389],[135,337],[405,233],[405,181],[360,207],[540,259],[585,233],[630,207],[585,181],[765,285],[720,311],[675,337],[720,363],[765,337],[720,415],[945,285],[990,311],[1035,337],[1035,285],[1035,233],[1080,259],[1080,311],[1080,363],[1125,337],[1125,389],[270,519],[225,545],[180,571],[180,519],[135,493],[135,545],[180,623],[225,597],[270,571],[315,545],[315,597],[630,623],[675,649],[720,675],[1215,285],[1215,233],[1215,181],[1260,207],[1305,181],[1305,129],[1395,233],[1350,259],[1305,285],[1260,259],[1305,233],[1350,207],[1350,311],[1395,285],[1395,337],[1440,311],[270,727],[225,753],[225,753],[180,727],[180,779],[135,753],[135,805],[135,857],[180,831],[225,805],[270,779],[315,805],[315,857],[270,831],[315,909],[270,883],[225,857],[990,831],[1035,805],[1080,779],[1125,753],[1035,857],[990,883],[990,935],[1035,909],[1080,883],[1125,857],[1125,805],[1080,831],[1170,779],[1215,805],[1170,831],[1215,753],[1170,883],[1215,909],[1260,935],[1305,909],[1305,857],[1305,805],[225,233],[180,207],[225,181],[270,207],[135,181],[180,155],[810,259],[540,155],[585,129],[1395,701],[1440,675],[1485,649],[1485,597],[1485,545],[1485,493],[1440,519],[1530,571],[1575,597],[1530,623],[1530,675],[1575,649],[1575,701],[1530,727],[1530,779],[1485,701],[1485,753],[1620,779],[1575,753],[1620,727],[1620,675],[1530,883],[1485,909],[1440,935],[1440,883],[1485,233],[1530,207],[1575,233],[1530,259],[1575,285],[1620,311],[1665,337],[1620,363],[1620,415],[1665,441],[1665,493],[1620,467],[1665,545],[1620,259],[1665,285],[1530,415],[1530,363],[1575,337],[1575,389],[1710,415],[135,129],[90,155],[90,363],[45,389],[0,415],[45,441],[90,415],[90,831],[45,857],[135,909],[180,987],[135,961],[90,987],[90,935],[225,1013],[180,1039],[450,935],[495,909],[495,961],[450,987],[495,1013],[540,1039],[540,987],[540,935],[585,961],[630,935],[720,1039],[765,1065],[810,1039],[810,1039],[855,1065],[810,1091],[900,1039],[810,1143],[855,1117],[900,1091],[765,1117],[720,1091],[945,1013],[990,1039],[945,1065],[1170,1039],[1215,1013],[1260,1039],[1305,1013],[1305,1065],[1260,1091],[1215,1065],[1170,1091],[1170,1091],[1215,1117],[1260,987],[1305,961],[1215,961],[1170,935],[1575,961],[1530,935],[1530,987],[1575,1013],[1530,1039],[1575,909],[1485,961],[450,571],[495,545],[1125,597],[90,207],[45,181],[765,545],[90,727],[1620,935],[1665,909],[1665,701],[855,805],[810,779],[1350,155],[1620,207],[1665,233],[1620,1039],[1440,1039],[1395,1013],[1395,961],[1440,987],[1485,1013],[360,1091],[360,1039],[315,1065],[270,1039],[225,1065],[180,1091],[585,493],[585,441],[0,831],[0,883],[45,701],[90,103],[1710,727],[1665,1065],[1665,1013],[1485,1065],[1440,1091],[1710,675],[1755,701],[1755,389],[1755,337],[1710,363],[1665,389],[1620,155],[1665,181],[1710,155],[1485,181],[945,233],[360,155],[225,129],[405,129],[540,779],[495,805],[405,857],[450,831],[450,779],[0,467],[45,493],[45,233],[360,103],[675,389],[1350,103],[1395,129],[810,207],[945,181],[990,207],[990,259],[1035,181],[720,207],[765,181],[765,233],[495,129],[450,155],[450,103],[405,77],[450,207],[495,181],[45,1013],[90,1039],[1170,155],[1215,129],[1215,77],[1440,103],[1620,103],[1665,129],[1530,103],[1530,51],[1710,935],[495,1065],[495,701],[540,675],[90,519],[90,571],[45,545],[540,207],[1260,155],[1620,987],[1665,961],[1665,1117],[1710,1091],[1710,1143],[1710,0],[1710,51],[1755,25],[180,103],[450,51],[405,25],[360,51],[90,779],[45,753],[90,675],[45,1065],[675,1065],[1440,259],[1485,285],[1530,311],[1485,129],[1440,51],[1485,77],[1350,831],[540,1091],[540,1143],[585,1117],[180,1143],[225,1117],[45,129],[45,77],[0,51],[45,25],[90,51],[1755,753],[1125,1065],[1125,1117],[360,0]];
	var allCoordsDistinct = _.uniq(allCoords, function(item) {
		return JSON.stringify(item);
	});

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
			var polygon = node.append("polygon")
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

			node.on("mousedown", function() { onNodeClick(polygon, nodeData); });
		});

		setOptimalZoom();
	}

	function onNodeClick(polygon, nodeData) {
		polygon.attr("fill-opacity", 0).attr("fill", "black");
		window.coords.push([nodeData.x, nodeData.y]);
	}

	function getCoordsForTeams(count) {
		var coords = [];
		for (var i=0; i<count; i++) {
			coords.push({"x": allCoordsDistinct[i][0], "y":  allCoordsDistinct[i][1]});
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
