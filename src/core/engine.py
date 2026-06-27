import glfw
from OpenGL.GL import *
import time
from typing import Any
from lib.events import Events
from src.core.event import EventManager
from src.core.input import Input
from src.core.scene import SceneManager
from src.core.window import Window
from src.graphics.camera import Camera
from src.core.scenes.battleground_scene import BattlegroundScene


class Engine:

    def __init__(
        self,
        window: Window,
        events: EventManager,
        scenes: SceneManager,
        camera: Camera,
        services: dict[str, Any],
    ):

        self.__window = window
        self.__events = events
        self.__scenes = scenes
        self.__camera = camera
        self.__services = services

        self.__events.subscribe(Events.ACTION_EXIT_GAME,
                                lambda _: self.__window.close_window())
        self.__events.subscribe(Events.TURN_END_REQUESTED,
                                self.__on_turn_end_requested)

        self.__is_running = True
        self.__last_frame_time = time.time()

        self.__input = Input(window)
        self.__input.bind(
            on_key=self.__on_key,
            on_mouse_move=self.__scenes.on_mouse_move,
            on_mouse_click=self.__on_mouse_click,
            on_mouse_press=self.__on_mouse_press,
            on_mouse_release=self.__on_mouse_release,
        )

    def __on_turn_end_requested(self, data: dict[str, Any]) -> None:
        if isinstance(self.__scenes.current, BattlegroundScene):
            self.__camera.rotate_perspective()

    def __on_key(self, key: int, action: int, mods: int) -> None:
        if action == glfw.PRESS:
            self.__scenes.on_key(key, action, mods)

    def __on_mouse_click(self, button: int, mx: float, my: float) -> None:
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.__scenes.on_mouse_click(button, mx, my)

    def __on_mouse_press(self, button: int, mx: float, my: float) -> None:
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.__scenes.on_mouse_press(mx, my)

    def __on_mouse_release(self, button: int, mx: float, my: float) -> None:
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.__scenes.on_mouse_release(mx, my)

    def run(self) -> None:
        while self.__is_running and not self.__window.should_close():
            dt = self.__tick()
            self.__window.poll_events()
            self.__update(dt)
            self.__render()
        self.__shutdown()

    def __update(self, dt: float) -> None:
        self.__camera.update(dt)      # lerp da rotação
        self.__scenes.update(dt)

    def __render(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.__scenes.render()
        self.__window.swap_buffers()

    def __tick(self) -> float:
        now = time.time()
        dt = now - self.__last_frame_time
        self.__last_frame_time = now
        return dt

    def __shutdown(self) -> None:
        self.__scenes.clear()
        self.__window.shutdown()

    def get(self, name: str):
        return self.__services.get(name)
