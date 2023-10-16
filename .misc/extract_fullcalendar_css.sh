#!/bin/sh
# Workaround for https://github.com/fullcalendar/fullcalendar/issues/7213
grep -r -h 'var css_' 'node_modules/fullcalendar-scheduler/index.global.js' 'node_modules/@fullcalendar/bootstrap/index.global.js' | sed 's/ *var css_[^ ]* = "\(.*\)";/\1/;s/\\"/"/g;s/\\\\/\\/g' > castellum/static/fullcalendar.css

name=$(grep -o 'injectStyles:[^,]\+' 'node_modules/fullcalendar-scheduler/index.global.min.js' | sed 's/injectStyles://')
sed "s/function $name(/function $name(){};function __nevercall(/" 'node_modules/fullcalendar-scheduler/index.global.min.js' > castellum/static/fullcalendar.js
