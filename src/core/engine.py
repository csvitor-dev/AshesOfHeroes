from OpenGL.GL import *
import time
from src.core.event import EventManager
from src.core.scene import SceneManager
from src.core.window import Window


class Engine:
    def __init__(self, width: int, height: int):
        self.__events = EventManager()
        self.__scenes = SceneManager(self.__events)
        self.__window = Window(width, height, self.__events)
        self.__is_running = True
        self.__last_frame_time = time.time()

    def run(self):
        while self.__is_running and not self.__window.should_close():
            current_time = time.time()
            dt = current_time - self.__last_frame_time
            self.__last_frame_time = current_time

            self.__window.poll_events()
            self.__update(dt)

            self.__render()
        self.__window.shutdown()

    def __update(self, dt: float):
        ...

    def __render(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.__scenes.render()

        self.__window.swap_buffers()
