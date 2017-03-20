#!/usr/bin/python3

import os
import sys
import subprocess


os.chdir('/home/guest/anonymine-performance')

query = os.getenv('QUERY_STRING', 'attempt-time-80@20x20')
assert not '/' in query
assert not '.' in query

sys.stdout.write('''Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html xlmns="http://www.w3.org/1999/xhtml">
    <head>
        <title>Graphs</title>
        <style>
            #body2
            {
                font-size: 2px;
                font-weight: bold;
            }
            pre
            {
                border: 1px solid #0000ff;
            }
        </style>
    </head>
    <body>
        <h1>Graphs</h1>
''')

args = ['./analyze.py'] + query.split(',')
n = len(args) - 1
body1 = subprocess.check_output(
    args, env={'LINES': str(24*n), 'COLUMNS': '80'}
).decode('ascii')
body2 = subprocess.check_output(
    args, env={'LINES': str(400*n), 'COLUMNS': '1000'}
).decode('ascii')
sys.stdout.write('<pre id="body1">'+body1+'</pre>\n')
sys.stdout.write('<pre id="body2">'+body2+'</pre>\n')

sys.stdout.write(''' </body>
</html>
''')

