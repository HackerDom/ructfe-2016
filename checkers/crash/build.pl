#!/usr/bin/perl

$service_name = "submarine_internal";
`g++ -I\$BREAKPAD/src -std=c++11 $service_name.cpp \$BREAKPAD/src/client/linux/libbreakpad_client.a -pthread -g -O0 -o $service_name`;
$module_info = `./dump_syms -i $service_name`;
$module_info =~ m/^MODULE\s\w+\s\w+\s(\w+)/;
$module_id = $1;
print "$module_id\n";
`mkdir symbols/$service_name`;
`mkdir symbols/$service_name/$module_id`;
`./dump_syms $service_name > symbols/$service_name/$module_id/$service_name.sym`;
