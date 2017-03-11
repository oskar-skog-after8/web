<?php

/* CONFIGURATION */
$wrap_conf = array(
    array("~^/oskar/cgiwrap\\.php(\\?test.*)?$~", "./test2.py"),
    array("~^.*\\?hello$~", "./ctest"),
);
$err_contact = "spam@example.com";


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
    $env = $_SERVER;
    $env['QUERY_STRING'] = make_query_string($_GET);
    $pipecfg = array(0 => array("pipe", "r"), 1 => array("pipe", "w"));
    $process = proc_open($script, $pipecfg, $pipes, NULL, $env);
    if (!is_resource($process))
    {
        error("Can't launch");
        return;
    }
    fwrite($pipes[0], make_query_string($_POST));
    fclose($pipes[0]);
    HTTP_response(stream_get_contents($pipes[1]));
    fclose($pipes[1]);
    proc_close($process);
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

