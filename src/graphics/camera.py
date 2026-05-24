from pyglm import glm
from OpenGL.GL import *
from lib.types import GameSide


class Camera:

    _PERSPECTIVES: dict[GameSide, dict[str, glm.vec3]] = {
        GameSide.BLUE: {
            "eye":    glm.vec3(0.0, -6.0, 5.0),
            "center": glm.vec3(0.0,  0.5, 0.0),
        },
        GameSide.RED: {
            "eye":    glm.vec3(0.0,  6.0, 5.0),
            "center": glm.vec3(0.0, -0.5, 0.0),
        },
    }

    _UP = glm.vec3(0.0, 0.0, 1.0)

    def __init__(
        self,
        width: int = 1280,
        height: int = 720,
        fov: float = 45.0,
        near: float = 0.1,
        far: float = 100.0
    ):
        self.width = width
        self.height = height
        self.fov = fov
        self.near = near
        self.far = far

        self._perspective = GameSide.BLUE
        self._rotating = False
        self._lerp_t = 1.0

        p = self._PERSPECTIVES[self._perspective]
        self._eye = glm.vec3(p["eye"])
        self._center = glm.vec3(p["center"])
        self._eye_target = glm.vec3(self._eye)
        self._center_target = glm.vec3(self._center)

    def rotate_perspective(self) -> None:
        self._perspective = GameSide.RED if self._perspective == GameSide.BLUE else GameSide.BLUE
        p = self._PERSPECTIVES[self._perspective]
        self._eye_target = glm.vec3(p["eye"])
        self._center_target = glm.vec3(p["center"])
        self._lerp_t = 0.0
        self._rotating = True

    @property
    def current_perspective(self) -> GameSide:
        return self._perspective

    @property
    def is_rotating(self) -> bool:
        return self._rotating

    def update(self, dt: float, speed: float = 3.5) -> None:
        if not self._rotating:
            return

        self._lerp_t = min(1.0, self._lerp_t + dt * speed)
        alpha = _ease_in_out(self._lerp_t)

        self._eye = glm.mix(self._eye, self._eye_target, alpha)
        self._center = glm.mix(self._center, self._center_target, alpha)

        if self._lerp_t >= 1.0:
            self._rotating = False

    def view(self) -> glm.mat4x4:
        return glm.lookAt(self._eye, self._center, self._UP)

    def projection(self) -> glm.mat4x4:
        aspect = self.width / max(self.height, 1)
        return glm.perspective(glm.radians(self.fov), aspect, self.near, self.far)

    def ortho(self) -> glm.mat4:
        return glm.ortho(0.0, float(self.width), float(self.height), 0.0, -1, 1)

    def upload_3d(self, program: int) -> None:
        """Sobe view + projection perspectiva + posição do eye."""
        _set_mat4(program, "u_view",       self.view())
        _set_mat4(program, "u_projection", self.projection())
        _set_vec3(program, "u_cam_pos",    glm.vec3(self._eye))

    def upload_2d(self, program: int) -> None:
        _set_mat4(program, "u_projection", self.ortho())

    def on_resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height


def _ease_in_out(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def _set_mat4(program: int, name: str, matrix: glm.mat4) -> None:
    loc = glGetUniformLocation(program, name)
    glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(matrix))


def _set_vec3(program: int, name: str, v: glm.vec3) -> None:
    loc = glGetUniformLocation(program, name)
    glUniform3fv(loc, 1, glm.value_ptr(v))
