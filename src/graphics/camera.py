from __future__ import annotations
import math
from pyglm import glm
from OpenGL.GL import *
from lib.types import GameSide


class Camera:
    _UP = glm.vec3(0.0, 0.0, 1.0)

    _EYE_RADIUS: float = 12.73
    _EYE_Z:      float = 10.0
    _EYE_TILT:   float = 0.5

    _ANGLE = {
        GameSide.BLUE: math.radians(270),
        GameSide.RED:  math.radians(90),
    }

    def __init__(
        self,
        width:  int = 1280,
        height: int = 720,
        fov:    float = 30.0,
        near:   float = 0.1,
        far:    float = 100.0,
    ):
        self.width = width
        self.height = height
        self.fov = fov
        self.near = near
        self.far = far

        self._perspective = GameSide.BLUE
        self._rotating = False
        self._angle_current = self._ANGLE[GameSide.BLUE]
        self._angle_target = self._angle_current
        self._lerp_t = 1.0

        self._eye, self._center = self._eye_center_from_angle(
            self._angle_current)

    def rotate_perspective(self) -> None:
        self._perspective = (
            GameSide.RED if self._perspective == GameSide.BLUE else GameSide.BLUE
        )
        self._angle_target = self._ANGLE[self._perspective]

        diff = self._angle_target - self._angle_current
        if diff > math.pi:
            self._angle_target -= 2 * math.pi
        elif diff < -math.pi:
            self._angle_target += 2 * math.pi

        self._lerp_t = 0.0
        self._rotating = True

    def update(self, dt: float, speed: float = 1.8) -> None:
        if not self._rotating:
            return

        self._lerp_t = min(1.0, self._lerp_t + dt * speed)
        alpha = _ease_in_out(self._lerp_t)

        self._angle_current = _lerp_angle(
            self._ANGLE[
                GameSide.BLUE if self._perspective == GameSide.RED else GameSide.RED
            ],
            self._angle_target,
            alpha,
        )

        self._eye, self._center = self._eye_center_from_angle(
            self._angle_current)

        if self._lerp_t >= 1.0:
            self._angle_current = self._angle_target
            self._rotating = False

    def _eye_center_from_angle(self, angle: float) -> tuple[glm.vec3, glm.vec3]:
        eye = glm.vec3(
            math.cos(angle) * self._EYE_RADIUS,
            math.sin(angle) * self._EYE_RADIUS,
            self._EYE_Z,
        )

        tilt_x = math.cos(angle) * self._EYE_TILT
        tilt_y = math.sin(angle) * self._EYE_TILT
        center = glm.vec3(-tilt_x, -tilt_y, 0.0)
        return eye, center

    def view(self) -> glm.mat4:
        return glm.lookAt(self._eye, self._center, self._UP)

    def projection(self) -> glm.mat4:
        aspect = self.width / max(self.height, 1)
        return glm.perspective(glm.radians(self.fov), aspect, self.near, self.far)

    def ortho(self) -> glm.mat4:
        return glm.ortho(0.0, float(self.width), float(self.height), 0.0, -1, 1)

    def upload_3d(self, program: int) -> None:
        _set_mat4(program, "projection", self.projection())
        _set_mat4(program, "camera", self.view())

    def upload_2d(self, program: int) -> None:
        _set_mat4(program, "projection", self.ortho())

    def on_resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    @property
    def current_perspective(self) -> GameSide:
        return self._perspective

    @property
    def is_rotating(self) -> bool:
        return self._rotating


def _lerp_angle(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _ease_in_out(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _set_mat4(program: int, name: str, matrix: glm.mat4) -> None:
    loc = glGetUniformLocation(program, name)
    glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(matrix))
