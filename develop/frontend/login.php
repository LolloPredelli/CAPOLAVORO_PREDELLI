<?php

include "php-utilities/connect.php";
include "php-utilities/functions.php";

session_start();

//if (isset($_SESSION['id'])) {
//    header("Location: personal_area.php");
//}

?>

<!DOCTYPE html>

<html lang="en">

<head>
    <title>mAInd map</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="stylesheets/login.css">
    <link href="https://fonts.cdnfonts.com/css/tt-ramillas-trl" rel="stylesheet"> <!-- font -->
</head>

<body>

    <?php
    if (isset($_POST['submit'])) {
        $email = mysqli_real_escape_string($db_conn, strtolower(filter_text($_POST['email'])));
        $pass = mysqli_real_escape_string($db_conn, hash('sha256', filter_text($_POST['password'])));


        $query_select = "SELECT id_user, fname, lname, email, pass FROM tuser WHERE email = '$email'";

        try {
            $select = @mysqli_query($db_conn, $query_select);
            if ($select) {
                $message = "utente trovato";
                $user_info = @mysqli_fetch_array($select);

                if ($pass == $user_info[4]) {
                    $message = "utente autenticato";

                    $_SESSION['id'] = $user_info[0];
                    $_SESSION['fname'] = $user_info[1];
                    $_SESSION['lname'] = $user_info[2];
                    $_SESSION['email'] = $user_info[3];
                    $_SESSION['pass'] = $user_info[4];

                    header("Location: personal_area.php");
                } else {
                    $message = "incorrect credential inserted";
                }
            } else {
                $message = "incorrect credential inserted";
            }
            //header("refresh:3; index.php");
            //header("Location: index.php");
        } catch (Exception $ex) {
            $message = $ex->getMessage();
        }
    }
    ?>
    <div class="grid-element">
        <h1>Enter in <span style="color: var(--primary);">your</span> personal <span
                style="color: var(--primary);">area</span></h1>
        <a href="index.html" id="home-btn"><button>HOME</button></a>
        <a href="signup.php"><button>SIGN UP</button></a>
    </div>
    <div class="grid-element" id="card">
        <h2>Log in</h2>
        <form action="<?= $_SERVER['PHP_SELF'] ?>" method="POST" class="flex-column gapy-1">
            <input type="email" name="email" id="email" placeholder="E-mail" required>
            <input type="password" name="password" id="password" placeholder="Password" required>
            <input type="submit" name="submit" id="submit" value="INVIA">
            <?= isset($message) ? $message : "" ?>
        </form>
    </div>
    <div class="mouse-shadow"></div>
    <script src="scripts/cursor.js"></script>
</body>

</html>