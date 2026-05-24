from __future__ import annotations
from OpenGL.GL import *
from pyglm import glm

from src.graphics.rendering.renderer import Renderer
from src.graphics.primitives.entity_3d import Entity3D
from src.graphics.primitives.prism import Prism
from src.graphics.primitives.sphere import Sphere
from src.graphics.primitives.cylinder import Cylinder


class ViewAegis:
    def __init__(self, renderer: Renderer):
        self._renderer = renderer
        self._objects: list[Entity3D] = []

    def load_assets(self) -> None:
        self._renderer.load_program("objects", "aegis")
        self._build_aegis(
            pos=glm.vec3(0, -1.5, 0),
            color=glm.vec4(0.9, 0.3, 0.3, 1.0),
        )
        self._build_aegis(
            pos=glm.vec3(0,  1.5, 0),
            color=glm.vec4(0.3, 0.5, 1.0, 1.0),
        )

    def unload_assets(self) -> None:
        for obj in self._objects:
            obj.delete()
        self._objects.clear()

    def _build_aegis(self, pos: glm.vec3, color: glm.vec4) -> None:
        prism = Prism(sides=6, radius=0.3, height=0.9)
        prism.position = pos
        prism.color = color

        crystal = Sphere(radius=0.18)
        crystal.position = glm.vec3(pos.x, pos.y, pos.z + 0.65)
        crystal.color = glm.vec4(color.x, color.y, color.z + 0.2, 1.0)

        base = Cylinder(radius=0.38, height=0.12)
        base.position = glm.vec3(pos.x, pos.y, pos.z - 0.5)
        base.color = glm.vec4(color.x * 0.6, color.y * 0.6, color.z * 0.6, 1.0)

        self._objects += [prism, crystal, base]

    def render(self, proj: glm.mat4) -> None:
        prog = self._renderer.use("objects_aegis")
        glUniformMatrix4fv(
            glGetUniformLocation(prog, "projection"),
            1, GL_FALSE, glm.value_ptr(proj),
        )
        for obj in self._objects:
            obj.draw(prog)
