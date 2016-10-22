#!/usr/bin/perl

$app_name = "test_app";
`g++ -I\$BREAKPAD/src -std=c++11 test_app.cpp \$BREAKPAD/src/client/linux/libbreakpad_client.a -pthread -g -O0 -o $app_name`;
$module_info = `./dump_syms -i $app_name`;
$module_info =~ m/^MODULE\s\w+\s\w+\s(\w+)/;
$module_id = $1;
print "$module_id\n";
`mkdir symbols/$app_name`;
`mkdir symbols/$app_name/$module_id`;
`./dump_syms $app_name > symbols/$app_name/$module_id/$app_name.sym`;
