<?php
const DB_HOST = 'localhost';
const DB_USER = 'root';
const DB_PASS = '';
const DB_NAME = 'mAInd_map';

try {
    $db_conn = @mysqli_connect(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    //$message = "connected";
} catch (Exception $e) {
    $error_message = $e->getMessage();
}
