<?php
include "php-utilities/connect.php";
include "php-utilities/functions.php";

session_start();

//check permissions

if (isset($_GET['map_id']) && isset($_SESSION['id'])) {
    $map_id = $_GET['map_id'];
    $user_id = $_SESSION['id'];
} else {
    header("Location: personal_area.php");
}


$query = "SELECT content FROM tmap WHERE id_map=" . $map_id . " AND fk_user=" . $user_id;
try {
    $result = mysqli_query($db_conn, $query);
    while ($row = @mysqli_fetch_array($result)) {
        $content = htmlspecialchars($row['content'], ENT_QUOTES, 'UTF-8');
    }
} catch (Exception $ex) {
    echo mysqli_error($db_conn);
}
?>

<!DOCTYPE html>
<html>

<head>
    <title>create map</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="stylesheets/show_map.css">
    <link href="https://fonts.cdnfonts.com/css/tt-ramillas-trl" rel="stylesheet"> <!-- font -->
</head>


<body>
    <a href="personal_area.php">
        <div id="back"></div>
    </a>
    <h4 id="result" style="display: none;"><?= $content ?></h4>
    <div class="span-container" id="spanContainer">
        <span id="span-title"></span>
    </div>
    <svg class="svg-container" id="svgContainer"></svg>
    <script src="scripts/show_map.js"></script>
    <div class="mouse-shadow"></div>
    <script src="scripts/cursor.js"></script>
</body>

</html>