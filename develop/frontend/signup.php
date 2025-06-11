<?php
include "php-utilities/connect.php";
include "php-utilities/functions.php";

session_start();

$errors = array();
$errors_field = array();
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

<body class="grad-black-bkg gridx-1-1 center-children padding-5">

    <?php
    if (isset($_POST['submit'])) {
        $fname = @mysqli_real_escape_string($db_conn, ucwords(strtolower(filter_text($_POST['fname']))));
        $lname = @mysqli_real_escape_string($db_conn, ucwords(strtolower(filter_text($_POST['lname']))));
        $email = @mysqli_real_escape_string($db_conn, strtolower(filter_text($_POST['email'])));
        $pass = @mysqli_real_escape_string($db_conn, filter_text($_POST['password']));

        if (!preg_match("/^[A-Za-z]+$/", $fname)) {
            array_push($errors, "First name only ammits letters");
            $errors_field['fname'] = true;
        }

        if (strlen($fname) < 2) {
            array_push($errors, "First name must be at least 2 letters");
            $errors_field['fname'] = true;
        }

        if (!preg_match("/^[A-Za-z]+$/", $lname)) {
            array_push($errors, "Last name only ammits letters");
            $errors_field['lname'] = true;
        }

        if (strlen($fname) < 2) {
            array_push($errors, "Last name must be at least 2 letters");
            $errors_field['lname'] = true;
        }

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            array_push($errors, "Email not valid");
            $errors_field['email'] = true;
        }

        if (strlen($pass) < 8) {
            array_push($errors, "Password must be at least 8 characters");
            $errors_field['pass'] = true;
        }

        if (!preg_match("@[A-Z]@", $pass)) {
            array_push($errors, "Password must contain at least an uppercase letter");
            $errors_field['pass'] = true;
        }

        if (!preg_match("@[a-z]@", $pass)) {
            array_push($errors, "Password must contain at least an lowercase letter");
            $errors_field['pass'] = true;
        }

        if (!preg_match('/[!@#$%^&*+~]/', $pass)) {
            array_push($errors, "The password must contain at least one special character");
            $errors_field['pass'] = true;
        }

        if (count($errors) == 0) {
            $hashed_password = hash('sha256', $pass);
            $query_insert = "INSERT INTO tuser (fname, lname, email, pass) "
                . "VALUES('$fname', '$lname', '$email', '$hashed_password')";

            try {
                $insert = @mysqli_query($db_conn, $query_insert);

                if ($insert) {
                    $message = "Contatto inserito con successo!";
                    $directory = "users/" . mysqli_insert_id($db_conn);
                    mkdir($directory);
                } else {
                    $message = "Contatto non inserito!";
                }

                header("Location: login.php");
            } catch (Exception $ex) {
                if (mysqli_errno($db_conn) == 1062) {
                    array_push($errors, "E-mail address already inserted");
                } else {
                    array_push($errors, "Problems with the server");
                }

                $message = @mysqli_error($db_conn);
            }
        }
    }

    ?>

    <div class="grid-element">
        <h1>Enter in <span style="color: var(--primary);">your</span> personal <span style="color: var(--primary);">area</span></h1>
        <a href="index.html" id="home-btn"><button>HOME</button></a>
        <a href="login.php"><button>LOG IN</button></a>
    </div>
    <div class="grid-element" id="card">
        <h2>Sign up</h2>
        <form action="<?= $_SERVER['PHP_SELF'] ?>" method="POST" class="flex-column gapy-1">
            <input type="text" name="fname" id="fname" value="<?= isset($fname) ? $fname : "" ?>" required
                class="<?= isset($errors['fname']) ? " red-bkg" : "" ?>" placeholder="First name">
            <input type="text" name="lname" id="lname" value="<?= isset($lname) ? $lname : "" ?>" required
                class="<?= isset($errors['lname']) ? " red-bkg" : "" ?>" placeholder="Last name">
            <input type="email" name="email" id="email" value="<?= isset($email) ? $email : ""  ?>" required
                class="<?= isset($errors['email']) ? " red-bkg" : "" ?>" placeholder="E-mail">
            <input type="password" name="password" id="password" required class="<?= isset($errors['pass']) ? " red-bkg"
                                                                                        : "" ?>" placeholder="Password">
            <?php if (count($errors) > 0) { ?>
                <div id="error-card">
                    Errors:
                    <ul>
                        <?php foreach ($errors as $e) { ?>
                            <li>
                                <?= $e ?>
                            </li>
                        <?php
                        }
                        ?>
                    </ul>
                </div>
            <?php } ?>
            <input type="submit" name="submit" id="submit">
            <?= isset($message) ? $message : "" ?>
        </form>
    </div>
    <div class="mouse-shadow"></div>
    <script src="scripts/cursor.js"></script>
</body>

</html>


















<?php
// check values
/*
        if (strlen($fname) <= 1 || strlen($fname) > 50) {
            $error = true;
            $errors["fname"] = "Invalid first name";
        }

        if (strlen($lname) <= 1 || strlen($lname) > 50) {
            $error = true;
            $errors["lname"] = "Invalid last name";
        }

        if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
            $error = true;
            $errors["email"] = "Insert a valid email (name@domain.dns)";
        }

        if (strlen($pass) < 8) {
            $error = true;
            $errors["pass"] = "The password is too short";
        }

        if (!preg_match("@[A-Z]@", $pass)) {
            $error = true;
            $errors["pass"] = "The password must contain at least one uppercase letter";
        }

        if (!preg_match("@[a-z]@", $pass)) {
            $error = true;
            $errors["pass"] = "The password must contain at least one lowercase letter";
        }

        if (!preg_match('/[!@#$%^&*+~]/', $pass)) {
            $error = true;
            $errors["pass"] = "The password must contain at least one special character";
        }
        */ ?>