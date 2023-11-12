<?php
$currentDir = './';
$dir = opendir($currentDir);
while (($file = readdir($dir)) !== false) {
    if ($file != '.' && $file != '..') {
        echo '<a href="' . $currentDir . $file . '">' . $file . '</a><br>';
    }
}

// 关闭文件夹
closedir($dir);