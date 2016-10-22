var Viz = function(infoData, startScoreboard) {
	var svgWrapperId = "svg-wrapper";
	var svgId = "svg-viz";
	var NOT_STARTED = "0";
	var PLAYING = "1";
	var SUSPEND = "2";
	var FINISHED = "3";
	var width = 800; // Это базовый размер экрана. Для остальных экранов используем zoom относительно этого размера.
	var height = 600; // TODO: Хороший вариант: 1366x662
	var loopDelayInMs = 1 * 1000; // TODO: 60 * 1000

	var info = infoData;
	var scoreboard = startScoreboard;
	var teams = [];
	var teamIdToNum = {};
	var nodes;
	var arrows;

	for (var fieldName in info.teams) {
		if (info.teams.hasOwnProperty(fieldName)) {
			var id = teams.length;
			teams.push({id: id, team_id: fieldName, name: info.teams[fieldName], score: 0, status: 0});
			teamIdToNum[fieldName] = teams.length - 1;
		}
	}
	updateScore();

	var svg = d3.select("#" + svgWrapperId).append("svg")
		.attr("version", "1.1")
		.attr("xmlns", "http://www.w3.org/2000/svg")
		.attr("id", svgId);
	var container = svg.append("g").classed("container", true);

	var zoom = d3.behavior.zoom().scaleExtent([0.25, 3]).size([width, height]).on("zoom", function () {
		container.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
	});
	svg.call(zoom);

	setOptimalZoom();
	drawTeams();
	loop();
	setInterval(loop, loopDelayInMs);

	function loop() {
		$.getJSON("./scoreboard").done(function (scoreboardData) {
			if (scoreboardData[1] === "success") {
				scoreboard = scoreboardData;
				updateScore();
			}
		});
		if (scoreboard.status != NOT_STARTED) {
			arrows = genRandomArrows(1);
			showArrows(arrows);
		}
	}

	function updateScore() {
		for (var i = 0; i < teams.length; i++) {
			teams[i].score = scoreboard.table[teams[i].team_id];
		}
	}

	function setOptimalZoom() {
		var $svg = $("#" + svgId);
		var realHeight = $svg.height();
		var realWidth = $svg.width();
		var scale = Math.min(realWidth / width, realHeight / height);
		var translate = [(realWidth - scale * width) / 2, (realHeight - scale * height) / 2];
		zoom.translate(translate).scale(scale).event(svg);
	}

	function showArrows(arrows) {
		container.selectAll(".arrow").remove();

		var links = container.selectAll(".arrow")
			.data(arrows)
			.enter()
			.append("g")
			.attr("class", "arrow");

		links.each(function () {
			var link = d3.select(this);
			var linkData = link.data()[0];
			var teamFrom = teams[linkData.from];
			var teamTo = teams[linkData.to];
			var fromX = teamFrom.x + teamFrom.size / 2;
			var fromY = teamFrom.y + teamFrom.size / 2;
			var toX = teamTo.x + teamTo.size / 2;
			var toY = teamTo.y + teamTo.size / 2;
			link.append("line")
				.classed("arrow-line", true)
				.attr("x1", fromX)
				.attr("y1", fromY)
				.attr("x2", toX)
				.attr("y2", toY);
		});
	}

	function drawTeams() {
		var columnsCount;
		var rowsCount;
		var islandSquareSide;
		var spaceBetweenIslands = 10;

		setIslandSize(teams.length);

		nodes = container.selectAll(".node")
			.data(teams)
			.enter()
			.append("g")
			.attr("class", "node");

		nodes.each(function () {
			var node = d3.select(this);
			var nodeData = node.data()[0];
			nodeData.x = (nodeData.id % columnsCount) * islandSquareSide + spaceBetweenIslands / 2;
			nodeData.y =  Math.floor(nodeData.id / columnsCount) * islandSquareSide + spaceBetweenIslands / 2;
			nodeData.size = islandSquareSide - spaceBetweenIslands;
			node.append("rect")
				.classed("island", true)
				.attr("width", nodeData.size)
				.attr("height", nodeData.size)
				.attr("transform", "translate(" + nodeData.x + ", " + nodeData.y + ")")
		});

		function setIslandSize(teamsCount) {
			islandSquareSide = 10;
			while (Math.floor(width / (islandSquareSide + 1)) * Math.floor(height / (islandSquareSide + 1)) > teamsCount)
				islandSquareSide++;
			columnsCount = Math.floor(width / islandSquareSide);
			rowsCount = Math.floor(height / islandSquareSide);
		}
	}

	function genRandomArrows(count) {
		var arrows = [];
		var i=0;
		while (i < count) {
			var from = randomInteger(0, teams.length - 1);
			var to = randomInteger(0, teams.length - 1);
			if (from != to) {
				i++;
				arrows.push({from: from, to: to});
			}
		}
		return arrows;
	}

	function randomInteger(min, max) {
		var rand = min + Math.random() * (max - min);
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
			var html = "<span>Team name: " + nodeData.name + "</span><br/>"
				+ "<span>Score: " + nodeData.score + "</span>";
			return "<div class='team-tooltip'>" + html + "</div>";
		},
		close: function () {
			$(".ui-helper-hidden-accessible").remove();
		}
	});

	return {
		getTeamsData: function() { return teams; },
		getInfo: function() { return info; },
		getScoreboard: function() { return scoreboard; }
	}
};
