import glfw
from OpenGL.GL import *
import time
from typing import Any
from src.core.event import EventManager
from src.core.scene import SceneManager
from src.core.window import Window
from src.graphics.camera import Camera


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

        self.__is_running = True
        self.__last_frame_time = time.time()

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
