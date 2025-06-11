<?php
include "php-utilities/connect.php";
include "php-utilities/functions.php";

session_start();

if (isset($_POST['logout'])) {
    session_unset();
    session_abort();
    header("Location: index.html");
}

if (isset($_POST['search'])) {
    $search = "%" . strtolower($_POST['search']) . "%";
} else {
    $search = "%%";
}

if (isset($_POST['delete_x'])) {
    $query_delete = 'DELETE FROM tmap WHERE id_map = ' . $_POST['index'];
    try {
        $delete = mysqli_query($db_conn, $query_delete);
        if ($delete) {
            $success['delete'] = "deletion succesful";
        } else {
            $error['delete'] = "deletion failed";
        }
    } catch (Exception $e) {
        $message = $ex->getMessage();
    }
}

if (isset($_POST['title'])) {
    $query_update = "UPDATE tmap SET title = '" . $_POST['title'] . "' WHERE id_map = " . $_POST['index'];
    try {
        $update = mysqli_query($db_conn, $query_update);
        if ($update) {
            $success['update'] = "update succesful";
        } else {
            $error['update'] = "update failed";
        }
    } catch (Exception $e) {
        $message = mysqli_error($db_conn);
    }
}



$query_select = 'SELECT id_map, title FROM tmap WHERE fk_user=' . $_SESSION["id"];
try {
    $select = mysqli_query($db_conn, $query_select);
} catch (Exception $e) {
    $message = $ex->getMessage();
}

?>

<!DOCTYPE html>

<html lang="en">

<head>
    <title>mAInd map</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="stylesheets/personal_area.css">
    <link href="https://fonts.cdnfonts.com/css/tt-ramillas-trl" rel="stylesheet"> <!-- font -->
</head>

<body>
    <header>
        <div id="create">
            <a href="new_map.php"><button>NEW MAP</button></a>
        </div>

        <div class="account">
            <form method="post" id="search-form">
                <input type="text" name="search" id="search" placeholder="search">
                <input type="image" alt="Submit" src="resources/images/search.svg" name="search-btn" id="search-btn" height="20" width="20">
            </form>
            <form method="post">
                <input type="submit" name="logout" id="logout" value="LOG OUT">
            </form>
            <a href="account_manage.php">
                <div id="user">
                </div>
            </a>
    </header>

    <main>
        <h1>Benvenuto
            <span style="color: var(--primary);"> <?= $_SESSION['fname'] ?></span>
        </h1>
        <div class="message-container">
            <?php if (isset($success['delete'])) { ?>
                <div class="success-card"><?= $success['delete'] ?></div>
            <?php } else if (isset($error['delete'])) { ?>
                <div class="error-card"><?= $error['delete'] ?></div>
            <?php } ?>

            <?php if (isset($success['update'])) { ?>
                <div class="success-card"><?= $success['update'] ?></div>
            <?php } else if (isset($error['update'])) { ?>
                <div class="error-card"><?= $error['update'] ?></div>
            <?php } ?>
        </div>
        <div id="maps-container">
            <?php
            if (isset($select)) {
                while ($row = @mysqli_fetch_array($select)) {
                    if (like_match($search, $row[1])) {
            ?>

                        <div class="map">
                            <form method="post">
                                <div class="options">
                                    <input type="image" src="resources/images/edit.svg" name="edit" class="input-option">
                                    <input type="image" src="resources/images/delete.svg" name="delete" class="input-option">
                                    <input type="hidden" name="index" value="<?= $row[0] ?>">
                                </div>
                            </form>
                            <a href="show_map.php?map_id=<?= $row[0] ?>">
                                <img src="resources/images/concept-map.svg" alt="">
                            </a>
                            <form method="post">
                                <input type="hidden" name="index" value="<?= $row[0] ?>">
                                <input type="text" name="title" id="map-title" <?= isset($_POST['edit_x']) && $_POST['index'] == $row[0] ? "" : "disabled" ?> value="<?= $row[1] ?>">
                            </form>
                        </div>

            <?php
                    }
                }
            } ?>
            <div class="map" id="add-map" onclick="location.replace('new_map.php')">
                <div><img src="resources/images/add.svg" alt=""></div>
                <input type="text" id="map-title" value="Create new" disabled>
            </div>
        </div>
    </main>
    <div class="mouse-shadow"></div>
    <script src="scripts/cursor.js"></script>
    <script src="scripts/map.js"></script>
</body>

</html>