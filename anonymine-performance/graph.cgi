#!/usr/bin/python3

import os
import sys
import subprocess


filename = os.getenv('QUERY_STRING')
assert not '/' in filename
assert not '.' in filename

os.chdir('/var/www/html/oskar/anonymine-performance')
body1 = subprocess.check_output(['./analyze.py', filename]).decode('ascii')
body2 = subprocess.check_output(
    ['./analyze.py', filename], env={'LINES': '400', 'COLUMNS': '1000'}
).decode('ascii')

sys.stdout.write('''Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html xlmns="http://www.w3.org/1999/xhtml">
    <head>
        <title>'''+filename+'''</title>
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
        <h1>'''+filename+'''</h1>
        <pre id="body1">'''+body1+'''</pre>
        <pre id="body2">'''+body2+'''</pre>
    </body>
</html>
''')

