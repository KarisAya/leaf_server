import "./style/index.less"

const ImagePath = window.location.origin + '/image';
document.getElementById('background')!.style.backgroundImage = `url(${ImagePath})`;

const InfoPath = window.location.origin + '/info';
const info = document.getElementById("info") as HTMLObjectElement;
info.data = InfoPath;

const ListPath = window.location.origin + '/list';
const list = document.getElementById("list") as HTMLObjectElement;
list.data = ListPath;