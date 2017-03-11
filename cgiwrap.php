<?php

/*
 * CGI wrapper in PHP
 *
 * This script is intended to be used on web servers where CGI support is
 * unavailable or disabled.
 *
 * NOTICE:  This requires the proc_open function.
 */

/*
 * Copyright (c) Oskar Skog, 2017
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1.  Redistributions of source code must retain the above copyright notice,
 *     this list of conditions and the following disclaimer.
 *
 * 2.  Redistributions in binary form must reproduce the above copyright notice,
 *     this list of conditions and the following disclaimer in the documentation
 *     and/or other materials provided with the distribution.
 *
 * This software is provided by the copyright holders and contributors "as is"
 * and any express or implied warranties, including, but not limited to, the
 * implied warranties of merchantability and fitness for a particular purpose
 * are disclaimed. In no event shall the copyright holder or contributors be
 * liable for any direct, indirect, incidental, special, exemplary, or
 * consequential damages (including, but not limited to, procurement of
 * substitute goods or services; loss of use, data, or profits; or business
 * interruption) however caused and on any theory of liability, whether in
 * contract, strict liability, or tort (including negligence or otherwise)
 * arising in any way out of the use of this software, even if advised of the
 * possibility of such damage.
 */


/*
 *      ***               ***
 *      *** CONFIGURATION ***
 *      ***               ***
 */

$err_contact = "spam@example.com";
/*
 * wrap_conf:
 * REQUEST_URI to script command substitution list
 *
 * The first regex pattern that mathces the REQUEST_URI will be used to
 * regex-substitute it to a shell command.  This shell command should be
 * the CGI script you wish to wrap.
 *
 * If you use URL rewriting, this one PHP script can wrap all your CGI
 * scripts.
 */
$wrap_conf = array(
    array("~^/oskar/cgiwrap\\.php(\\?test.*)?$~", "./test2.py"),
    array("~^.*\\?hello$~", "./ctest"),
);

/*
 *      ***                   ***
 *      *** CONFIGURATION END ***
 *      ***                   ***
 */


function error($msg)
{
    global $err_contact;
    $msg = htmlspecialchars($msg);
    http_response_code(500);
    header("Content-Type: text/html");
    echo <<<END
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8">
        <title>ERROR (cgiwrap.php)</title>
        <meta name="robots" content="noindex"/>
        <meta name="viewport" content="width=device-width"/>
        <style type="text/css">
            h2
            {
                margin-top: 3.1416em;
            }
            pre
            {
                word-wrap: break-word;
                white-space: pre-wrap;
            }
            $media only screen and (max-width: 640px)
            {
                pre
                {
                    font-size: 80%;
                }
            }
        </style>
    </head>
    <body>
        <h1>ERROR (cgiwrap.php)</h1>
        <p>
            Please send a link to this page to
            <a href="mailto:$err_contact">$err_contact</a>.
        </p>
        <h2>Error message</h2>
        <pre>$msg</pre>
    </body>
</html>
END;
}

/*
 * Turn an array("foo" => "bar", "baz" => "quux") into a query string
 * like "foo=bar&baz=quux"
 *
 * This will be used to write $_POST to stdin of the wrapped CGI script.
 * And to store $_GET in the environment variable QUERY_STRING
 */
function make_query_string($request_array)
{
    $query_string = "";
    foreach ($request_array as $parameter => $value)
        $query_string .= "&".urlencode($parameter)."=".urlencode($value);
    return substr($query_string, 1);
}

/*
 * Parse a HTTP response and recreate it with PHP.
 *
 * Accepts response code:
 *    - A: Status header: "Status: 404 Not Found"
 *    - B: Response status line: "HTTP/1.1 404 Not Found"
 *    - If both are present, the Status header will dominate.
 */
function HTTP_response($raw)
{
    $fragments = explode("\n\n", $raw, 2);
    $HTTP_headers = $fragments[0];
    $HTTP_body = $fragments[1];
    foreach (explode("\n", $HTTP_headers) as $HTTP_header)
    {
        $fragments = explode(":", $HTTP_header, 2);
        if ($fragments[0] == "Status")
        {
            http_response_code(intval($fragments[1]));
        }
        else
            header($HTTP_header);
    }
    echo $HTTP_body;
}

/* Inner main function. */
function wrap($script)
{
    /*
     * $_SERVER is pretty much the same as the environment variables sent
     * to CGI scripts.
     */
    $env = $_SERVER;
    $env['QUERY_STRING'] = make_query_string($_GET);
    /* TODO:  Check if QUERY_STRING needs to be overriden. */
    
    $pipecfg = array(
        0 => array("pipe", "r"), /* POST parameters */
        1 => array("pipe", "w"),
        2 => array("pipe", "w"), /* error handling */
    );
    $process = proc_open($script, $pipecfg, $pipes, NULL, $env);
    if (!is_resource($process))
    {
        error("proc_open failed");
        return;
    }
    
    /*
     * CGI scripts read the HTTP body from stdin. POST parameters are
     * stored in the HTTP body using the same syntax as GET parameter.
     */
    fwrite($pipes[0], make_query_string($_POST));
    fclose($pipes[0]);
    
    $stdout = stream_get_contents($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($process);
    /*
     * proc_open doesn't fail even if the script does.
     * If no data was returned, something probably went wrong and the
     * reason is on stderr.
     */
    if ($stdout)
        HTTP_response($stdout);
    else
        error("CGI execution failed\n\n" . $stderr);
}

function main()
{
    $me = $_SERVER['REQUEST_URI'];
    global $wrap_conf;
    foreach ($wrap_conf as $record)
    {
        $pattern = $record[0];
        $replacement = $record[1];
        if (preg_match($pattern, $me))
        {
            wrap(preg_replace($pattern, $replacement, $me));
            return;
        }
    }
    error("No regex matches: $me");
}

main();

