document.addEventListener("DOMContentLoaded", () => {
    let inputEvents = [];

    addEventListener("mousedown", (e) => {
        inputEvents.push({
            mouseX: e.pageX, mouseY: e.pageY,
            buttons: e.buttons
        });
    });

    addEventListener("contextmenu", (e) => {
        e.preventDefault();
    });

    addEventListener("mouseup", (e) => {
        inputEvents.push({
            mouseX: e.pageX, mouseY: e.pageY,
            buttons: e.buttons
        });
    });

    /*addEventListener("mousemove", (e) => {
        inputEvents.push({
            mouseX: e.pageX, mouseY: e.pageY
        });
    });*/

    function mapKeyEvent(e) {
        if (e.ctrlKey && e.shiftKey && e.code == "KeyR") {
            return;
        }
        e.preventDefault();
        if (e.key.length == 1) {
            return e.key;
        }
        return {
            "Alt": "\ue00a",
            "Control": "\ue009",
            "Meta": "\ue03d",
            "Shift": "\ue008",
            "Enter": "\ue007",
            "Tab": "\ue004",
            "ArrowDown": "\ue015",
            "ArrowLeft": "\ue012",
            "ArrowRight": "\ue014",
            "ArrowUp": "\ue013",
            "End": "\ue010",
            "Home": "\ue011",
            "PageDown": "\ue00f",
            "PageUp": "\ue00e",
            "Backspace": "\ue003"
        }[e.key];
    }

    addEventListener("keydown", (e) => {
        inputEvents.push({
            keydown: mapKeyEvent(e)
        });
    });

    addEventListener("keyup", (e) => {
        inputEvents.push({
            keyup: mapKeyEvent(e)
        });
    });

    new ResizeObserver(entries => {
        for (const entry of entries) {
            const size = entry.contentBoxSize[0];
            inputEvents.push({
                viewportSize: [
                    size.inlineSize,
                    size.blockSize
                ]
            });
        }
    }).observe(document.getElementById("web-viewport"));

    const img = document.getElementById("img");

    const ws = new WebSocket("wss://solid-space-computing-machine-4w4wr7jxx9qhjw64-7775.app.github.dev/");

    function sendUpdate() {
        ws.send(JSON.stringify({input: inputEvents}));
        inputEvents = [];
    }

    ws.addEventListener("open", () => {
        sendUpdate();
    });

    ws.addEventListener("error", () => {
        alert("something went wrong");
    });

    ws.addEventListener("message", (e) => {
        const message = JSON.parse(e.data);
        img.src = "webpage.png?" + (+new Date());
        img.style.display = "unset";
        setTimeout(sendUpdate, 100);
    });
});
