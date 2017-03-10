<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <title>Test</title>
        <meta name="robots" content="noindex"/>
    </head>
    <body>
        <h1>Read POST body</h1>
        <pre>
<?php
echo "hidden: ".$_POST['hidden']."\n";
echo "text: ".$_POST['text']."\n";
echo "check: ".$_POST['check']."\n";
echo "textbox: ".$_POST['textbox']."\n";
?>
        </pre>
        <h1>Write POST body</h1>
        <form action="test.php" method="POST">
            <input type="hidden" name="hidden" value="secret"/>
            <input type="text" name="text"/>
            <input type="checkbox" name="check"/><br/>
            <textarea name="textbox" cols="80" rows="24"></textarea>
            <input type="submit"/>
        </form>
    </body>
</html>



