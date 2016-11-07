#pragma once

#define NEWLINE "\r\n"

#define LINE(s) s NEWLINE

#define RESPONSE \
	LINE("HTTP/1.1 200 OK") \
	LINE("Content-Type: text/html") \
	LINE("")

#define BODY \
	LINE("<html>") \
	LINE("<head>") \
  	LINE("	<title>Weather center</title>") \
	LINE("</head>") \
	LINE("<body>") \
	LINE("	<h1>Today: %d&deg;C, %s</h1>") \
	LINE("	<h3>5-day forecast:</h1>") \
	LINE("	<p>%d&deg;C, %s</p>") \
	LINE("	<p>%d&deg;C, %s</p>") \
	LINE("	<p>%d&deg;C, %s</p>") \
	LINE("	<p>%d&deg;C, %s</p>") \
	LINE("	<p>%d&deg;C, %s</p>") \
	LINE("	<p></p>") \
	LINE("	<p><em>Signature: %016llx</em></p>") \
	LINE("</body>") \
	LINE("</html>")
