<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <meta name="robots" content="noindex, nofollow"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <style type="text/css">
        </style>

<?php
/*
CREATE TABLE messages (subject VARCHAR(200) CHARACTER SET utf8 UNIQUE, message TEXT CHARACTER SET utf8, hidden ENUM('true', 'false'));
*/


function SQL_escape($x)
{
    return str_replace("'", "''", $x);
}


function read_message($db)
{
    $subject = htmlspecialchars($_REQUEST['subject']);
    $key = SQL_escape($_REQUEST['subject']);
    $result = $db->query("SELECT message FROM messages WHERE subject='$key';");
    $message = htmlspecialchars($result->fetch_assoc()['message']);
    if ($db->affected_rows)
    {
        echo <<<END
        <title>$subject</title>
    </head>
    <body>
        <h1>$subject</h1>
<pre>
$message
</pre>
        <form action="messages.php" method="POST">
            <input type="hidden" name="action" value="delete"/>
            <input type="hidden" name="subject" value="$subject"/>
            <input type="submit" value="Delete this message"/>
        </form>
END;
    } else
    {
        echo <<<END
        <title>Message not found</title>
    </head>
    <body>
        <h1>Message not found</h1>
END;
    }
    echo "        <p><a href='messages.php'>Main page</a></p>\n";
}


function save_message($db)
{
    $subject = SQL_escape($_REQUEST['subject']);
    $message = SQL_escape($_REQUEST['message']);
    if ($_REQUEST['hidden'] == 'on')
        $hidden = 'true';
    else
        $hidden = 'false';
    $db->query("INSERT INTO messages SET " .
        "subject='$subject', message='$message', hidden='$hidden';");
    if ($db->errno)
    {
        $message = htmlspecialchars($_REQUEST['message']);
        echo <<<END
        <title>Subject occupied</title>
    </head>
    <body>
        <h1>Subject occupied</title>
        <p>You need to choose another subject line.</p>
        <form>
            <input type="hidden" name="action" value="save"/>
            Subject: <input type="text" name="subject"/>
            Hidden: <input type="checkbox" name="hidden"/><br/>
            <textarea name="message" cols="80" rows="24">$message</textarea>
            <br/><input type="submit"/>
        </form>
        <p><a href='messages.php'>Main page</a></p>
END;
    } else
    {
        $subject = htmlspecialchars(urlencode($_REQUEST['subject']));
        echo <<<END
        <meta http-equiv="Refresh"
            content="0; url=messages.php?action=read&amp;subject=$subject"/>
    </head>
    <body>
END;
    }
}


function delete_message($db)
{
    $key = SQL_escape($_REQUEST['subject']);
    $subject = htmlspecialchars('"' . $_REQUEST['subject'] . '"');
    $db->query("DELETE FROM messages WHERE subject='$key';");
    echo <<<END
        <meta http-equiv="Refresh" content="0; url=messages.php"/>
    </head>
    <body>
END;
}


function main_page($db)
{
    echo <<<END
        <title>Messages - PHP &amp; MySQL experiment</title>
        <h1>Messages - PHP &amp; MySQL experiment</h1>
        <form action="messages.php" method="POST">
            <input type="hidden" name="action" value="save"/>
            <h2>Write a new message</h2>
            Subject: <input type="text" name="subject"/>
            Hidden: <input type="checkbox" name="hidden"/>
            <br/>
            <textarea name="message" cols="80" rows="24"></textarea>
            <br/>
            <input type="submit"/>
        </form>
END;
    echo <<<END
        <title>All subjects</title>
    </head>
    <body>
        <h2>Read messages</h2>
        <form action="messages.php" method="POST">
            <h3>Read a (hidden) message</h3>
            <input type="hidden" name="action" value="read"/>
            Subject: <input type="text" name="subject"/>
            <input type="submit" value="Read"/>
        </form>
        <h3>List of all non-hidden messages</h3>
        <p>
END;
    $result = $db->query("SELECT subject FROM messages WHERE hidden='false';");
    while ($row = $result->fetch_assoc())
    {
        $subject = htmlspecialchars($row['subject']);
        $subject_param = urlencode($row['subject']);
        echo "\n            "; /* Indent HTML correctly. */
        echo "<a href='messages.php?action=read&amp;subject=$subject_param'>";
        echo "$subject</a><br/>";
    }
    echo "\n        </p>\n";
}


function main()
{
    /* Import $db_user and $db_password. */
    require_once "auth.php";
    $db = new mysqli("localhost", $db_user, $db_password, "messages");
    if ($db->connect_errno)
    {
        $err = $db->connect_error;
        echo <<<END
        <title>Failed to connect to MySQL</title>
    </head>
    <body>
        <h1>Failed to connect to MySQL</h1>
        <p>$err</p>
    </body>
</html>
END;
     exit();
    }
    
    switch ($_REQUEST['action'])
    {
        case "read": read_message($db); break;
        case "save": save_message($db); break;
        case "delete": delete_message($db); break;
        default: main_page($db);
    }
}

main();

?>

    </body>
</html>

