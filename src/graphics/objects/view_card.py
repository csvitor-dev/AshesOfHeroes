from OpenGL.GL import *
from pyglm import glm
from typing import Any
from src.graphics.rendering.renderer import Renderer
from src.graphics.vertex import VertexLayout, VertexAttribute
# from src.graphics.texture_manager import TextureManager
# from src.graphics.camera import _set_mat4


# layout de vértice: posição 2D + UV
_LAYOUT = VertexLayout([
    VertexAttribute("position", GL_FLOAT, 2),
    VertexAttribute("uv",       GL_FLOAT, 2),
])

_QUAD_INDICES = [0, 1, 2, 2, 3, 0]


class ViewCard:

    W = 80.0
    H = 110.0

    def __init__(
        self,
        card_id:      object,
        texture_path: str,
        renderer:     Renderer,
        textures:     Any,  # TextureManager,
        position:     glm.vec2,
    ):
        self.card_id = card_id
        self.texture_path = texture_path
        self.renderer = renderer
        self.textures = textures

        self.position = glm.vec2(position)
        self._target = glm.vec2(position)

        self.scale = glm.vec2(1.0, 1.0)
        self.alpha = 1.0
        self.glow = 0.0

        self._vao_name = f"card_{card_id}"
        self._upload_quad()

    def _upload_quad(self):
        import numpy as np
        x, y = 0.0, 0.0
        w, h = self.W, self.H

        verts = np.array([
            x,   y,   0.0, 0.0,
            x+w, y,   1.0, 0.0,
            x+w, y+h, 1.0, 1.0,
            x,   y+h, 0.0, 1.0,
        ], dtype=np.float32)

        indices = np.array(_QUAD_INDICES, dtype=np.uint32)
        self.renderer.upload(self._vao_name, verts, _LAYOUT, indices)

    def move_to(self, target: glm.vec2):
        self._target = glm.vec2(target)

    def update_lerp(self, dt: float, speed: float = 8.0):
        alpha = min(1.0, speed * dt)
        self.position = glm.mix(self.position, self._target, alpha)

    @property
    def is_moving(self) -> bool:
        return glm.distance(self.position, self._target) > 0.5

    def draw(self, program: int, projection: glm.mat4):
        model = glm.mat4(1.0)
        model = glm.translate(model, glm.vec3(self.position, 0.0))
        model = glm.scale(model, glm.vec3(self.scale, 1.0))

        _set_mat4(program, "u_model", model)
        _set_mat4(program, "u_projection", projection)

        loc = glGetUniformLocation(program, "u_alpha")
        glUniform1f(loc, self.alpha)

        loc = glGetUniformLocation(program, "u_glow")
        glUniform1f(loc, self.glow)

        loc = glGetUniformLocation(program, "u_texture")
        glUniform1i(loc, 0)

        self.textures.bind(self.texture_path, slot=0)
        self.renderer.draw(self._vao_name)

    def delete(self):
        self.renderer.delete(self._vao_name)
