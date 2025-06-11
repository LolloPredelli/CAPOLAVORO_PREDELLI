<?php
include "php-utilities/connect.php";
include "php-utilities/functions.php";

session_start();

//check permissions

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['result']) && $_POST['result'] != "") {
        $content = mysqli_real_escape_string($db_conn, $_POST['result']);
        $title = filter_text($_POST['title']);
        $fk_user = $_SESSION['id'];

        $query_insert = "INSERT INTO tmap(title, content, fk_user) VALUES('$title', '" . $content . "', '$fk_user');";
        try {
            $result = mysqli_query($db_conn, $query_insert);

            if ($result) {
                echo "mappa creata";
                header("Location: show_map.php?map_id=" . mysqli_insert_id($db_conn));
            } else {
                echo "errore nella creazione della mappa";
            }
        } catch (Exception $ex) {
            echo mysqli_error($db_conn);
        }
    }

    if (isset($_POST['logout'])) {
        session_unset();
        session_abort();
        header("Location: index.html");
    }
}
?>

<!DOCTYPE html>
<html>

<head>
    <title>create map</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="stylesheets/new_map.css">
    <link href="https://fonts.cdnfonts.com/css/tt-ramillas-trl" rel="stylesheet"> <!-- font -->
</head>

<body>
    <header>
        <div id="home">
            <a href="personal_area.php"><button>HOME</button></a>
        </div>

        <div class="account">
            <form method="post">
                <input type="submit" name="logout" id="logout" value="LOG OUT">
            </form>
            <div id="user">
            </div>
    </header>


    <main>
        <h1>Insert a <span style="color: var(--primary);">text</span> to be transformed into a <span style="color: var(--primary);">mind map</span></h1>
        <form id="input-text" name="input-text" method="post">
            <input type="hidden" name="result" value="">
            <input type="hidden" name="title" value="">
            <textarea name="text" placeholder="Insert your text here..."></textarea>
            <div id="buttons">
                <div>
                    <input type="image" src="resources/images/deletePrimary.svg" onclick="this.form.reset()">
                </div>
                <div>
                    <input id="send" type="image" src="resources/images/send.svg">
                </div>
            </div>
        </form>
    </main>
    <script src="scripts/request-API.js"></script>
</body>

</html>