import "./style/index.less"

const home = document.getElementById("home")!;
home.addEventListener("click", () => { window.location.href = 'home' });

const server = document.getElementById("server")!;
server.addEventListener("click", () => { window.location.href = 'server' });

const doc = document.getElementById("doc")!;
doc.addEventListener("click", () => { window.location.href = 'doc' });