<?php

function filter_text($text)
{
    return addslashes(filter_var(trim($text), FILTER_SANITIZE_FULL_SPECIAL_CHARS));
}

function like_match($pattern, $subject)
{
    $pattern = str_replace('%', '.*', preg_quote($pattern, '/'));
    return (bool) preg_match("/^{$pattern}$/i", $subject);
}
// https://stackoverflow.com/questions/4912294/php-like-thing-similar-to-mysql-like-for-if-statemen
