<?php

/* CONFIGURATION */
$wrap_conf = array(
    "/.*/" => "./ctest",
);

function error($msg)
{
    echo "<pre>".htmlspecialchars($msg)."</pre>";
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
    foreach ($wrap_conf as $regex => $script)
    {
        if (preg_match($regex, $me))
        {
            wrap($script);
            return;
        }
    }
    error("No match");
}

main();

