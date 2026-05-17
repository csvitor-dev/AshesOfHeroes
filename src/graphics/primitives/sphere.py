import numpy as np
import math
from src.graphics.primitives import Entity3D


class Sphere(Entity3D):
    def __init__(self, radius: float = 0.25, stacks: int = 12, slices: int = 16):
        super().__init__()
        self.radius = radius
        self.stacks = stacks
        self.slices = slices
        self._build_geometry()

    def _build_geometry(self):
        verts: list[float] = []
        idxs: list[int] = []

        for s in range(self.stacks + 1):
            phi = math.pi * s / self.stacks
            for sl in range(self.slices + 1):
                theta = 2 * math.pi * sl / self.slices

                x = math.sin(phi) * math.cos(theta)
                y = math.cos(phi)
                z = math.sin(phi) * math.sin(theta)

                verts += [
                    x * self.radius, y * self.radius, z * self.radius,
                    x, y, z,         # normal = posição normalizada
                ]

        for s in range(self.stacks):
            for sl in range(self.slices):
                a = s * (self.slices + 1) + sl
                b = (s + 1) * (self.slices + 1) + sl
                idxs += [a, b, a + 1,  b, b + 1, a + 1]

        self._upload(
            np.array(verts, dtype=np.float32),
            np.array(idxs,  dtype=np.uint32),
        )
