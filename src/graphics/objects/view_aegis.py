from OpenGL.GL import *
from pyglm import glm

from src.graphics.rendering.renderer import Renderer
from src.graphics.primitives.hero_aegis import HeroAegis


class ViewAegis:
    def __init__(self, renderer: Renderer):
        self._renderer = renderer
        self._objects: list[HeroAegis] = []

    def load_assets(self) -> None:
        self._renderer.load_program("objects", "aegis")
        self._build_aegis(
            pos=glm.vec3(0.0, 4.7, 0.0),
            color_body=(0.90, 0.30, 0.30),
        )
        self._build_aegis(
            pos=glm.vec3(0.0, -4.7, 0.0),
            color_body=(0.30, 0.30, 0.90),
        )

    def unload_assets(self) -> None:
        for obj in self._objects:
            obj.delete()
        self._objects.clear()

    def _build_aegis(
        self,
        pos:        glm.vec3,
        color_body: tuple[float, float, float],
    ) -> None:
        aegis = HeroAegis(color_body=color_body)
        aegis.position = pos
        self._objects.append(aegis)

    def render(self, proj: glm.mat4, view: glm.mat4) -> None:
        prog = self._renderer.use("objects_aegis")

        glUniformMatrix4fv(
            glGetUniformLocation(prog, "projection"),
            1, GL_FALSE, glm.value_ptr(proj),
        )
        glUniformMatrix4fv(
            glGetUniformLocation(prog, "camera"),
            1, GL_FALSE, glm.value_ptr(view),
        )

        for obj in self._objects:
            obj.draw(prog)
