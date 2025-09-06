from selenium import webdriver
from selenium.webdriver.support.events import AbstractEventListener, EventFiringWebDriver
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
import asyncio
from websockets.asyncio.server import serve
import json


with open("inject.js") as file:
    INJECT_JS = file.read()


TARGET = "https://duckduckgo.com"


class EventListener(AbstractEventListener):
    def after_navigate_to(self, url, driver: webdriver.Firefox):
        driver.execute_script(INJECT_JS)


def start_firefox() -> webdriver.Firefox:
    profile = webdriver.FirefoxProfile()
    required_perms = ["geo"]
    for perm in required_perms:
        # 1 indicated 'always allow'
        profile.set_preference(f"permissions.default.{perm}", 1)
    options = webdriver.FirefoxOptions()
    options.profile = profile
    options.add_argument("--headless")
    return EventFiringWebDriver(webdriver.Firefox(options), EventListener())


mouse_x = 0
mouse_y = 0
buttons = 0


def process_input(input, ff: webdriver.Firefox):
    global mouse_x, mouse_y, buttons
    builder = ActionBuilder(ff)
    for frame in input:
        new_mouse_x = frame.get("mouseX", mouse_x)
        new_mouse_y = frame.get("mouseY", mouse_y)
        new_buttons = frame.get("buttons", buttons)

        if (mouse_x, mouse_y) != (new_mouse_x, new_mouse_y):
            builder.pointer_action.move_to_location(
                new_mouse_x, new_mouse_y
            )

        for btn in range(5):
            mask = 1 << btn
            if new_buttons & mask and not buttons & mask:
                builder.pointer_action.pointer_down(btn)
            elif buttons & mask and not new_buttons & mask:
                builder.pointer_action.pointer_up(btn)

        if "keydown" in frame:
            builder.key_action.key_down(frame["keydown"])
        if "keyup" in frame:
            builder.key_action.key_up(frame["keyup"])

        mouse_x = new_mouse_x
        mouse_y = new_mouse_y
        buttons = new_buttons
        builder.pointer_action.pause(0.02)
        builder.key_action.pause(0.02)
    builder.perform()

async def main(websocket):
    print("Got request ...")
    ff = start_firefox()
    print("Firefox started ...")
    ff.get(TARGET)
    async for message in websocket:
        request = json.loads(message)
        print(request)
        process_input(request["input"], ff)
        ff.save_screenshot("html/webpage.png")
        await websocket.send(json.dumps({}))
    ff.quit()


async def start_websocket_server():
    host = "0.0.0.0"
    port = 7775
    print(f"Serving websocket {host} port {port} (http://{host}:{port}/) ... ")
    async with serve(main, host, port) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(start_websocket_server())
