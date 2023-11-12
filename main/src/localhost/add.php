<?php
$a = isset($_GET['a']) ? $_GET['a'] : 0;
$b = isset($_GET['b']) ? $_GET['b'] : 0;
$sum = $a + $b;
$result = array('add' => $sum);
echo json_encode($result);