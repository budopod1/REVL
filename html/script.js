document.addEventListener("DOMContentLoaded", () => {
    window.REVL_INJECTED = true;

    let inputEvents = [];

    const viewportElem = document.getElementById("web-viewport");

    const urlBar = document.getElementById("url-bar");

    viewportElem.addEventListener("mousedown", (e) => {
        inputEvents.push({
            mouseX: e.offsetX, mouseY: e.offsetY,
            buttons: e.buttons
        });
    });

    viewportElem.addEventListener("contextmenu", (e) => {
        e.preventDefault();
    });

    viewportElem.addEventListener("mouseup", (e) => {
        inputEvents.push({
            mouseX: e.offsetX, mouseY: e.offsetY,
            buttons: e.buttons
        });
    });

    /*viewportElem.addEventListener("mousemove", (e) => {
        inputEvents.push({
            mouseX: e.offsetX, mouseY: e.offsetY
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

    viewportElem.addEventListener("keydown", (e) => {
        inputEvents.push({
            keydown: mapKeyEvent(e)
        });
    });

    viewportElem.addEventListener("keyup", (e) => {
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
    }).observe(viewportElem);

    document.getElementById("back-btn").addEventListener("click", () => {
        inputEvents.push({back: true});
    });

    document.getElementById("forward-btn").addEventListener("click", () => {
        inputEvents.push({forward: true});
    });

    document.getElementById("reload-btn").addEventListener("click", () => {
        inputEvents.push({reload: true});
    });

    document.getElementById("url-form").addEventListener("submit", e => {
        e.preventDefault();
        inputEvents.push({url: urlBar.value});
    });

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
        if (message.url) {
            urlBar.value = message.url;
        }
        img.src = "webpage.png?" + (+new Date());
        img.style.display = "unset";
        setTimeout(sendUpdate, 100);
    });
});
