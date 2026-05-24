from typing import Any
from pyglm import glm
from OpenGL.GL import *
from src.graphics.objects.view_board import ViewBoard
from src.graphics.texture_manager import TextureManager
from src.graphics.rendering.renderer import Renderer
from src.graphics.rendering.hud_renderer import HudRenderer
from src.graphics.primitives.entity_3d import Entity3D
from src.graphics.primitives.cylinder import Cylinder
from src.graphics.primitives.prism import Prism
from src.graphics.primitives.sphere import Sphere


LAYOUT_POS2D = None


class BoardRenderer:

    def __init__(
        self,
        renderer: Renderer,
        textures: TextureManager,
        view_board: ViewBoard,
        hud: HudRenderer,
    ):
        self.renderer = renderer
        self.textures = textures
        self.view_board = view_board
        self.hud = hud

        self._build_aegis()
        self._load_shaders()

    def _load_shaders(self):
        self.renderer.load_program("aegis", "model")

    def _build_aegis(self):
        self._aegis_opp: list[Entity3D] = [
            self._make_prism(pos=glm.vec3(0, 0, -1.5),
                             color=glm.vec4(0.9, 0.3, 0.3, 1)),
            self._make_sphere(pos=glm.vec3(0, 0.65, -1.5),
                              color=glm.vec4(1.0, 0.6, 0.6, 1)),
            self._make_cylinder(pos=glm.vec3(0, -0.5, -1.5),
                                color=glm.vec4(0.5, 0.2, 0.2, 1)),
        ]
        self._aegis_pl: list[Entity3D] = [
            self._make_prism(pos=glm.vec3(0, 0, 1.5),
                             color=glm.vec4(0.3, 0.5, 1.0, 1)),
            self._make_sphere(pos=glm.vec3(0, 0.65, 1.5),
                              color=glm.vec4(0.5, 0.8, 1.0, 1)),
            self._make_cylinder(pos=glm.vec3(0, -0.5, 1.5),
                                color=glm.vec4(0.2, 0.3, 0.6, 1)),
        ]
        self._all_3d = self._aegis_opp + self._aegis_pl

    @staticmethod
    def _make_prism(pos: glm.vec3, color: glm.vec4):
        p = Prism(sides=6, radius=0.3, height=0.9)
        p.position, p.color = pos, color
        return p

    @staticmethod
    def _make_sphere(pos: glm.vec3, color: glm.vec4):
        s = Sphere(radius=0.18)
        s.position, s.color = pos, color
        return s

    @staticmethod
    def _make_cylinder(pos: glm.vec3, color: glm.vec4):
        c = Cylinder(radius=0.38, height=0.12)
        c.position, c.color = pos, color
        return c

    def update(self, dt: float):
        self.view_board.update(dt)

    def render(self, game_state: Any) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._render_3d()
        self._render_2d()
        self.hud.render(game_state)

    def _render_3d(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        prog = self.renderer.use("aegis")

        for obj in self._all_3d:
            obj.draw(prog)

    def _render_2d(self):
        glDisable(GL_DEPTH_TEST)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.view_board.render()

    def on_resize(self, width: int, height: int):
        glViewport(0, 0, width, height)

    def delete(self):
        for obj in self._all_3d:
            obj.delete()
        self.view_board.unload_assets()
