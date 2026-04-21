import glfw
from OpenGL.GL import *
import numpy as np


def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def setup() -> dict:
    glClearColor(0.1, 0.1, 0.1, 1)


def render():
    glClear(GL_COLOR_BUFFER_BIT)


def main():
    glfw.init()
    window = glfw.create_window(
        800,
        600,
        "Ashes of Heroes",
        None,
        None
    )
    glfw.make_context_current(window)
    setup()

    width, height = glfw.get_framebuffer_size(window)
    glViewport(0, 0, width, height)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
