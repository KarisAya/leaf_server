<?php
function getRandomFile($folderPath) {
    // 获取目标文件夹中的所有文件列表
    $files = glob($folderPath . '/*');
    if (empty($files)) {return false;}
    $randomIndex = rand(0, count($files) - 1);
    $randomFile = $files[$randomIndex];
    return $randomFile;
}
$imagePath = getRandomFile('./image');
// 检查文件是否存在
if ($imagePath === false) {
    header('HTTP/1.0 404 Not Found');
    echo '404 Not Found';
}else{
    header('Content-Type: image/jpeg');
    readfile($imagePath);
}
exit;