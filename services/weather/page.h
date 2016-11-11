#pragma once

#define NEWLINE "\r\n"

#define LINE(s) s NEWLINE

#define RESPONSE \
	LINE("HTTP/1.1 200 OK") \
	LINE("Content-Type: text/html") \
	LINE("")

#define BODY \
	LINE("<!doctype html>") \
	LINE("<html lang=\"en-US\">") \
	LINE("	<head>") \
	LINE("		<meta charset=\"utf-8\">") \
	LINE("		<!--[if IE]><meta http-equiv=\"X-UA-Compatible\" content=\"IE=edge\"><![endif]-->") \
	LINE("		<title>Weather center • Atlantis • RuCTFE 2016</title>") \
	LINE("		<meta name=\"description\" content=\"Weather center\">") \
	LINE("		<meta name=\"keywords\" content=\"Atlantis, RuCTFE, Weather center\">") \
	LINE("		<meta name=\"author\" content=\"Hackerdom, hackerdom.ru, Krait\">") \
	LINE("		<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">") \
	LINE("		<link rel=\"shortcut icon\" href=\"/static/ico/weather.ico\" type=\"image/x-icon\">") \
	LINE("		<link rel=\"stylesheet\" href=\"/static/lib/bootstrap/css/bootstrap.min.css\">") \
	LINE("		<link rel=\"stylesheet\" href=\"/static/css/atlantis.css\">") \
	LINE("		<link rel=\"stylesheet\" href=\"/static/css/weather.css\">") \
	LINE("	</head>") \
	LINE("	<body class=\"service-page wt-body\" data-spy=\"scroll\" data-target=\"#main-navbar\">") \
	LINE("		<div class=\"page-loader\"></div>") \
	LINE("		<div class=\"body\">") \
	LINE("			<header id=\"header\" class=\"header-main\">") \
	LINE("				<nav id=\"main-navbar\" class=\"navbar navbar-default navbar-fixed-top\" role=\"navigation\">") \
	LINE("					<div class=\"container\">") \
	LINE("						<div class=\"navbar-header\">") \
	LINE("							<button type=\"button\" class=\"navbar-toggle collapsed\" data-toggle=\"collapse\" data-target=\"#bs-navbar-collapse\"></button>") \
	LINE("							<a class=\"navbar-brand\" href=\"/home\">Atlantis</a>") \
	LINE("							<a class=\"navbar-brand navbar-brand-service\" href=\"/\">Weather center</a>") \
	LINE("						</div>") \
	LINE("					</div>") \
	LINE("				</nav>") \
	LINE("			</header>") \
	LINE("			<section class=\"main-block\">") \
	LINE("				<div class=\"container\">") \
	LINE("					<div class=\"caption\">") \
	LINE("						<div class=\"row\">") \
	LINE("							<div class=\"col-sm-2 center-block\">") \
	LINE("								<a href=\"/\">") \
	LINE("									<img src=\"/static/logos/weather.svg\" class=\"logo img-responsive\">") \
	LINE("								</a>") \
	LINE("							</div>") \
	LINE("							<div class=\"col-sm-10 content-block\">") \
	LINE("								<div class=\"page-header wt-header\">") \
	LINE("									<h1>Weather in Atlantis</h1>") \
	LINE("								</div>") \
	LINE("								<div class=\"well wt-well\">") \
	LINE("									<h2>Today:</h2>") \
	LINE("									<div class=\"wt-block-large\">") \
	LINE("										<div class=\"wt-temp-large\">%d&deg;C</div>") \
	LINE("										<img class=\"wt-icon-large\" src=\"/static/img/weather/%s.png\" />") \
	LINE("									</div>") \
	LINE("									<h3>5-day forecast:</h1>") \
	LINE("									<div class=\"wt-block-small\">") \
	LINE("										<div class=\"wt-temp-small\">%d&deg;C</div>") \
	LINE("										<img class=\"wt-icon-small\" src=\"/static/img/weather/%s.png\" />") \
	LINE("									</div>") \
	LINE("									<div class=\"wt-block-small\">") \
	LINE("										<div class=\"wt-temp-small\">%d&deg;C</div>") \
	LINE("										<img class=\"wt-icon-small\" src=\"/static/img/weather/%s.png\" />") \
	LINE("									</div>") \
	LINE("									<div class=\"wt-block-small\">") \
	LINE("										<div class=\"wt-temp-small\">%d&deg;C</div>") \
	LINE("										<img class=\"wt-icon-small\" src=\"/static/img/weather/%s.png\" />") \
	LINE("									</div>") \
	LINE("									<div class=\"wt-block-small\">") \
	LINE("										<div class=\"wt-temp-small\">%d&deg;C</div>") \
	LINE("										<img class=\"wt-icon-small\" src=\"/static/img/weather/%s.png\" />") \
	LINE("									</div>") \
	LINE("									<div class=\"wt-block-small\">") \
	LINE("										<div class=\"wt-temp-small\">%d&deg;C</div>") \
	LINE("										<img class=\"wt-icon-small\" src=\"/static/img/weather/%s.png\" />") \
	LINE("									</div>") \
	LINE("									<div class=\"wt-signature\"><em>Signature: %016llx</em></div>") \
	LINE("								</div>") \
	LINE("							</div>") \
	LINE("						</div>") \
	LINE("					</div>") \
	LINE("				</div>") \
	LINE("			</section>") \
	LINE("		</div>") \
	LINE("		<script src=\"/static/lib/jquery/jquery-3.1.1.min.js\"></script>") \
	LINE("		<script src=\"/static/lib/bootstrap/js/bootstrap.min.js\"></script>") \
	LINE("		<script src=\"/static/js/atlantis.js\"></script>") \
	LINE("	</body>") \
	LINE("</html>")


#define CBODY \
	LINE("Current weather forecast:") \
	LINE("") \
	LINE("Today: %d*C, %s") \
	LINE("") \
	LINE("Next 5 days:") \
	LINE("    - %d*C, %s") \
	LINE("    - %d*C, %s") \
	LINE("    - %d*C, %s") \
	LINE("    - %d*C, %s") \
	LINE("    - %d*C, %s") \
	LINE("") \
	LINE("Signature: %016llx")
