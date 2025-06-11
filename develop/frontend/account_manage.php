<?php
include "php-utilities/connect.php";
include "php-utilities/functions.php";

session_start();

// get data from session
$id = $_SESSION['id'];
$fname = $_SESSION['fname'];
$lname = $_SESSION['lname'];
$email = $_SESSION['email'];
$password = $_SESSION['pass'];

// form handling
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['save'])) {
        $errors_field = array();

        // get post data
        isset($_POST['fname']) ? $fname = filter_text($_POST['fname']) : $error = "error fname";
        isset($_POST['lname']) ? $lname = filter_text($_POST['lname']) : $error = "error lname";
        isset($_POST['email']) ? $email = filter_text($_POST['email']) : $error = "error email";

        if (!preg_match("/^[A-Za-z]+$/", $fname)) {
            $errors_field['fname'] = "First name only ammits letters";
        }

        if (strlen($fname) < 2) {
            $errors_field['fname'] = "First name must be at least 2 letters";
        }

        if (!preg_match("/^[A-Za-z]+$/", $lname)) {
            $errors_field['lname'] = "Last name only ammits letters";
        }

        if (strlen($fname) < 2) {
            $errors_field['lname'] = "Last name must be at least 2 letters";
        }

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $errors_field['email'] = "Email not valid";
        }

        $query_insert = "UPDATE tuser SET fname='$fname', lname='$lname', email='$email'";

        if (isset($_POST['oldpassword'])) {
            if ($_POST['oldpassword'] != "" && $_POST['newpassword'] != "" && $_POST['confirmpassword'] != "") {
                if (hash('sha256', $_POST['oldpassword']) == $password) {
                    isset($_POST['newpassword']) ? $newpassword = hash('sha256', $_POST['newpassword']) : $error = "error newpassword";
                    isset($_POST['confirmpassword']) ? $confirmpassword = hash('sha256', $_POST['confirmpassword']) : $error = "error confirmpassword";


                    if (strlen($newpassword) < 8) {
                        $errors_field['pass'] = "Password must be at least 8 characters";
                    }

                    if (!preg_match("@[A-Z]@", $newpassword)) {
                        $errors_field['pass'] = "Password must contain at least an uppercase letter";
                    }

                    if (!preg_match("@[a-z]@", $newpassword)) {
                        $errors_field['pass'] = "Password must contain at least an lowercase letter";
                    }

                    if (!preg_match('/[!@#$%^&*+~]/', $newpassword)) {
                        $errors_field['pass'] = "The password must contain at least one special character";
                    }

                    if ($newpassword == $confirmpassword) {
                        $query_insert = $query_insert . ", pass='$newpassword'";
                    } else {
                        $errors_field['confirmpass'] = "Passwords don't match";
                    }
                } else {
                    $errors_field['oldpass'] = "Password incorrect";
                }
            }
        }

        $query_insert = $query_insert . " WHERE id_user=$id;";
        $query_select = "SELECT * FROM tuser WHERE id_user=$id";

        if (count($errors_field) == 0) {
            try {
                $result = mysqli_query($db_conn, $query_insert);

                if ($result) {
                    $success = "data updated correctly";
                    $result = mysqli_query($db_conn, $query_select);
                    $user_info = mysqli_fetch_array($result);

                    $_SESSION['id'] = $user_info[0];
                    $_SESSION['fname'] = $user_info[1];
                    $_SESSION['lname'] = $user_info[2];
                    $_SESSION['email'] = $user_info[3];
                    $_SESSION['pass'] = $user_info[4];
                } else {
                    $errors_field['fname'] = "errore nell'aggiornamento";
                }
            } catch (Exception $ex) {
                $errors_field['fname'] = mysqli_error($db_conn);
            }
        }
    } else if (isset($_POST['cancel'])) {
        header("Location: personal_area.php");
    }

    if (isset($_POST['logout'])) {
        session_unset();
        session_abort();
        header("Location: index.html");
    }
}
?>


<!DOCTYPE html>

<html lang="en">

<head>
    <title>mAInd map</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="stylesheets/manage_account.css">
    <link href="https://fonts.cdnfonts.com/css/tt-ramillas-trl" rel="stylesheet"> <!-- font -->
</head>

<body>
    <header>
        <div id="create">
            <a href="personal_area.php"><button>HOME</button></a>
        </div>

        <div class="account">
            <form method="post">
                <input type="submit" name="logout" id="logout" value="LOG OUT">
            </form>
    </header>


    <form id="change-info" method='post'>
        <div id="title">
            <div id="user"></div>
            <h1>Account <span style="color: var(--primary);">settings</span></h1>
        </div>

        <?php if (isset($success)) { ?>
            <div class="success-card"><?= $success ?></div>
        <?php } ?>

        <div class="left-border">
            <h2>Personal data</h2>
            <?php if (isset($errors_field['fname'])) { ?>
                <div class="error-card"><?= $errors_field['fname'] ?></div>
            <?php } ?>
            <input type="text" name="fname" value="<?= $fname ?>" placeholder="first name">

            <?php if (isset($errors_field['lname'])) { ?>
                <div class="error-card"><?= $errors_field['lname'] ?></div>
            <?php } ?>
            <input type="text" name="lname" value="<?= $lname ?>" placeholder="last name">

            <?php if (isset($errors_field['email'])) { ?>
                <div class="error-card"><?= $errors_field['email'] ?></div>
            <?php } ?>
            <input type="email" name="email" value="<?= $email ?>" placeholder="email">
        </div>

        <div class="left-border">
            <h2>Change password</h2>
            <?php if (isset($errors_field['oldpass'])) { ?>
                <div class="error-card"><?= $errors_field['oldpass'] ?></div>
            <?php } ?>
            <input type="password" name="oldpassword" placeholder="insert current password">

            <?php if (isset($errors_field['pass'])) { ?>
                <div class="error-card"><?= $errors_field['pass'] ?></div>
            <?php } ?>
            <input type="password" name="newpassword" placeholder="new password">

            <?php if (isset($errors_field['confpass'])) { ?>
                <div class="error-card"><?= $errors_field['confpass'] ?></div>
            <?php } ?>
            <input type="password" name="confirmpassword" placeholder="confirm password">
        </div>



        <div id="buttons">
            <input type="submit" name="save" value="save">
            <input type="submit" name="cancel" value="cancel">
        </div>
    </form>
    <div class="mouse-shadow"></div>
    <script src="scripts/cursor.js"></script>
</body>

</html>