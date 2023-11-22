import "./style/index.less"

document.getElementById('background')!.style.backgroundImage = `url(${'/image'})`;

const list = document.getElementById("list") as HTMLObjectElement;
list.data = '/list';

const output = document.getElementById("output") as HTMLDivElement;
const input_text = document.getElementById("input_text") as HTMLInputElement;
const input_button = document.getElementById("input_button") as HTMLButtonElement;

input_button.addEventListener('click', () => { sendData(input_text.value) });
input_text.addEventListener('keydown', (event) => { if (event.key === 'Enter') { sendData(input_text.value) } });

function sendData(command: string) {
    if (command === "") { return }
    const requestOptions: RequestInit = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: command,
    };
    output.innerHTML += command
    input_text.value = ""
    fetch('/terminal', requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            let resp: string;
            if (data.contect === "") { resp = `<br>${data.path}> ` }
            else { resp = `<br>${data.contect} <br>${data.path}> ` }
            output.innerHTML += resp
            output.scrollTop = output.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
        })
}
sendData("init")