#!/usr/bin/python

import os
import sys


def htmlescape(s):
    s = s.replace('&', '&amp;')
    s = s.replace('<', '&lt;')
    s = s.replace('>', '&gt;')
    return s

def main():
    sys.stdout.write('Content-Type: application/xhtml+xml\n\n')
    sys.stdout.write('''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <title>Test</title>
        <meta name="robots" content="noindex"/>
    </head>
    <body>
        <h1>Test</h1>
        <dl>
        
        <dt>GET parameters</dt>
        <dd><pre>{}</pre></dd>
        
        <dt>Read POST body</dt>
        <dd><pre>{}</pre></dd>
        
        <dt>Write POST body</dt>
        <dd><form action="cgiwrap.php" method="POST">
            <input type="hidden" name="hidden" value="secret"/>
            <input type="text" name="text"/>
            <input type="checkbox" name="check"/><br/>
            <textarea name="textbox" cols="80" rows="24"/>
            <input type="submit"/>
        </form></dd>
        
        </dl>
    </body>
</html>
    '''.format(
        htmlescape(os.getenv('QUERY_STRING', '')),
        htmlescape(sys.stdin.read())
    ))


if __name__ == '__main__':
    main()



