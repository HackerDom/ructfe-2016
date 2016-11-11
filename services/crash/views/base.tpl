<!doctype html>
<html lang="en-US">
	<head>
		<meta charset="utf-8">
		<!--[if IE]><meta http-equiv="X-UA-Compatible" content="IE=edge"><![endif]-->
		<title>Crash • Atlantis • RuCTFE 2016</title>
		<meta name="description" content="Crash reports from submarine's internal services">
		<meta name="keywords" content="Atlantis, RuCTFE, Crash">
		<meta name="author" content="Hackerdom, hackerdom.ru, Ruslan Kutdusov, vorkulsky">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="shortcut icon" href="/static/ico/crash.ico" type="image/x-icon">
		<link rel="stylesheet" href="/static/lib/bootstrap/css/bootstrap.min.css">
		<link rel="stylesheet" href="/static/css/atlantis.css">
	</head>
	<body class="service-page" data-spy="scroll" data-target="#main-navbar">
		<div class="page-loader"></div>
		<div class="body">
			<header id="header" class="header-main">
				<nav id="main-navbar" class="navbar navbar-default navbar-fixed-top" role="navigation">
					<div class="container">
						<div class="navbar-header">
							<button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse"></button>
							<a class="navbar-brand" href="/home">Atlantis</a>
							<a class="navbar-brand navbar-brand-service" href="/">Crash</a>
						</div>
						<div class="collapse navbar-collapse" id="bs-navbar-collapse"></div>
					</div>
				</nav>
			</header>
			<section class="main-block">
				<div class="container">
					<div class="caption">
						<div class="row">
							<div class="col-sm-2 center-block">
								<a href="/">
									<img src="/static/logos/crash.svg" class="logo img-responsive">
								</a>
							</div>
							<div class="col-sm-8 content-block">
								<h1>Crash</h1>
								<div class="well">
									Crash reports from submarine's internal services
								</div>
								<div class="extra-space-l"></div>
								<div id="sevice-content-wrapper">
									{{!base}}
								</div>
							</div>
						</div>
					</div>
				</div>
			</section>
		</div>

		<script src="/static/lib/jquery/jquery-3.1.1.min.js"></script>
		<script src="/static/js/crash.js"></script>
	</body>
</html>
