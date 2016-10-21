var Viz = function() {
	var svgWrapperId = "svg-wrapper";
	var svgId = "svg-viz";

	var svg;
	var container;
	var zoom;
	var teams = [];
	var width = 800; // Это базовый размер экрана. Для остальных экранов используем zoom относительно этого размера.
	var height = 600; // Хороший вариант: 1366x662
	var nodes;
	var arrows;

	function init() {
		svg = d3.select("#" + svgWrapperId).append("svg")
			.attr("version", "1.1")
			.attr("xmlns", "http://www.w3.org/2000/svg")
			.attr("id", svgId);
		container = svg.append("g").classed("container", true);

		zoom = d3.behavior.zoom().scaleExtent([0.25, 3]).size([width, height]).on("zoom", function () {
			container.attr("transform", "translate(" + d3.event.translate + ")" + " scale(" + d3.event.scale + ")");
		});
		svg.call(zoom);

		setOptimalZoom();
		drawTeams();

		arrows = genRandomArrows(60);
		showArrows(arrows);
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

	function genTeams(count) {
		for (var i = 0; i<count; i++) {
			var team = {
				id: i
			};
			teams.push(team);
		}
	}

	function genRandomArrows(count) {
		var arrows = [];
		var i=0;
		while (i < count) {
			var from = randomInteger(0, teams.length);
			var to = randomInteger(0, teams.length);
			if (from != to) {
				i++;
				arrows.push({from: from, to: to});
			}
		}
		return arrows;
	}

	function randomInteger(min, max) {
		var rand = min + Math.random() * (max - min)
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
			var text = nodeData.id + "";
			return "<div class='team-tooltip'>" + text + "</div>";
		},
		close: function () {
			$(".ui-helper-hidden-accessible").remove();
		}
	});

	return {
		init: init,
		genTeams: genTeams,
		getTeamsData: function() { return teams; }
	}
};
