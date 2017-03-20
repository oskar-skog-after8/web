#!/usr/bin/python3

import os
import sys
import subprocess


os.chdir('/var/www/html/oskar/anonymine-performance')

query = os.getenv('QUERY_STRING', 'attempt-time-80@20x20')
assert not '/' in query
assert not '.' in query

sys.stdout.write('''Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html xlmns="http://www.w3.org/1999/xhtml">
    <head>
        <title>Graphs</title>
        <style>
            .body2
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

for filename in query.split(','):
    body1 = subprocess.check_output(['./analyze.py', filename]).decode('ascii')
    body2 = subprocess.check_output(
        ['./analyze.py', filename], env={'LINES': '400', 'COLUMNS': '1000'}
    ).decode('ascii')
    sys.stdout.write('''        <h2>'''+filename+'''</h2>
        <pre class="body1">'''+body1+'''</pre>
        <pre class="body2">'''+body2+'''</pre>
''')

sys.stdout.write(''' </body>
</html>
''')

