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
    def __init__(self, interface):
        self.interface = interface

    def after_navigate_to(self, url, driver: webdriver.Firefox):
        pass
        # self.interface.push_update({"url": url})
        # driver.execute_script(INJECT_JS)


class FFInterface:
    def __init__(self):
        self.updates = {}
        self.ff: webdriver.Firefox = self._start_firefox()
        self.chrome_height: int = self._calculate_chrome_height()
        self.mouse_x = 0
        self.mouse_y = 0
        self.buttons = 0
        self.url = None

    def _start_firefox(self) -> webdriver.Firefox:
        profile = webdriver.FirefoxProfile()
        required_perms = ["geo"]
        for perm in required_perms:
            # 1 indicates 'always allow'
            profile.set_preference(f"permissions.default.{perm}", 1)
        options = webdriver.FirefoxOptions()
        options.profile = profile
        options.add_argument("--headless")
        listener = EventListener(self)
        return EventFiringWebDriver(webdriver.Firefox(options), listener)
    
    # chrome in this case referring to the non-browser parts of the window, not Google Chrome
    def _calculate_chrome_height(self) -> int:
        self.ff.get("data:text/html,")
        requested_height = 720
        self.ff.set_window_size(1280, requested_height)
        effective_height = self.ff.execute_script("return window.innerHeight;")
        return requested_height - effective_height
    
    def process_frame(self, builder, frame):
        new_mouse_x = frame.get("mouseX", self.mouse_x)
        new_mouse_y = frame.get("mouseY", self.mouse_y)
        new_buttons = frame.get("buttons", self.buttons)

        if (self.mouse_x, self.mouse_y) != (new_mouse_x, new_mouse_y):
            builder.pointer_action.move_to_location(
                new_mouse_x, new_mouse_y
            )

        for btn in range(5):
            mask = 1 << btn
            if new_buttons & mask and not self.buttons & mask:
                builder.pointer_action.pointer_down(btn)
            elif self.buttons & mask and not new_buttons & mask:
                builder.pointer_action.pointer_up(btn)

        if "keydown" in frame:
            builder.key_action.key_down(frame["keydown"])
        if "keyup" in frame:
            builder.key_action.key_up(frame["keyup"])
        
        if "viewportSize" in frame:
            viewport_x, viewport_y = frame["viewportSize"]
            self.ff.set_window_size(
                viewport_x, viewport_y + self.chrome_height
            )
        
        if frame.get("back", False):
            self.ff.back()
        
        if frame.get("forward", False):
            self.ff.forward()
        
        if frame.get("reload", False):
            self.ff.refresh()
        
        url = frame.get("url", None)
        if url is not None:
            self.set_url(url)

        self.mouse_x = new_mouse_x
        self.mouse_y = new_mouse_y
        self.buttons = new_buttons
        builder.pointer_action.pause(0.02)
        builder.key_action.pause(0.02)
    
    def js_communicate(self):
        is_injected, url = self.ff.execute_script(
            "return [!!window.REVL_INJECTED, location.href];"
        )
        if url != self.url:
            self.url = url
            self.push_update({"url": url})
        if not is_injected:
            self.ff.execute_script(INJECT_JS)
    
    def push_update(self, data):
        self.updates.update(data)
    
    def get_updates(self):
        updates = self.updates
        self.updates = {}
        return updates
    
    def process_input(self, input):
        builder = ActionBuilder(self.ff)
        for frame in input:
            self.process_frame(builder, frame)
        
        builder.perform()
    
    def set_url(self, url: str):
        self.ff.get(url)
    
    def get_url(self) -> str:
        return self.listener.url
    
    def take_screenshot(self):
        self.ff.save_screenshot("html/webpage.png")
    
    def quit(self):
        self.ff.quit()


async def main(websocket):
    print("Got request ...")
    interface = FFInterface()
    print("Firefox started ...")
    interface.set_url(TARGET)
    async for message in websocket:
        request = json.loads(message)
        print(request)
        interface.js_communicate()
        interface.process_input(request["input"])
        interface.take_screenshot()
        await websocket.send(json.dumps(interface.get_updates()))
    interface.quit()


async def start_websocket_server():
    host = "0.0.0.0"
    port = 7775
    print(f"Serving websocket {host} port {port} (http://{host}:{port}/) ... ")
    async with serve(main, host, port) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(start_websocket_server())
