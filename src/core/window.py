import glfw
from OpenGL.GL import *
import sys
from lib.events import EventType
from core.event import EventManager


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


class Window:
    def __init__(self, width: int, height: int, event_manager: EventManager):
        self.__width = width
        self.__height = height
        self.__title = "Ashe of Heroes"
        self.__events = event_manager
        self.__handle = None

        self.__initialize_glfw()

    def __initialize_glfw(self):
        if not glfw.init():
            raise Exception("Failed to initialize GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

        self.__handle = glfw.create_window(
            self.__width, self.__height, self.__title, None, None)

        if not self.__handle:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        glfw.make_context_current(self.__handle)
        glClearColor(0.1, 0.1, 0.1, 1)

        width, height = glfw.get_framebuffer_size(self.__handle)
        glViewport(0, 0, width, height)
        glfw.set_framebuffer_size_callback(
            self.__handle, framebuffer_size_callback)

        glfw.set_key_callback(self.__handle, self._key_callback)
        glfw.set_mouse_button_callback(
            self.__handle, self._mouse_button_callback)

        glfw.swap_interval(1)

    def _key_callback(self, window, key, scancode, action, mods):
        if action == glfw.PRESS:
            self.__events.emit(EventType.RAW_INPUT_KEY, key=key, action="PRESS")

    def _mouse_button_callback(self, window, button, action, mods):
        if action == glfw.PRESS:
            x, y = glfw.get_cursor_pos(window)
            self.__events.emit(EventType.RAW_INPUT_MOUSE, button=button, x=x, y=y)

    def poll_events(self):
        glfw.poll_events()

    def should_close(self):
        return glfw.window_should_close(self.__handle)

    def swap_buffers(self):
        glfw.swap_buffers(self.__handle)

    def shutdown(self):
        glfw.terminate()
