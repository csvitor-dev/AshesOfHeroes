import numpy as np
import math
from src.graphics.primitives.entity_3d import Entity3D


class Prism(Entity3D):
    def __init__(self, sides: int = 6, radius: float = 0.4, height: float = 1.2):
        super().__init__()
        self.sides = sides
        self.radius = radius
        self.height = height
        self._build_geometry()

    def _build_geometry(self):
        verts: list[float] = []
        idxs: list[int] = []

        step = 2 * math.pi / self.sides
        h = self.height / 2

        for i in range(self.sides):
            a = i * step
            x = math.cos(a) * self.radius
            z = math.sin(a) * self.radius

            nx, nz = math.cos(a + step / 2), math.sin(a + step / 2)

            verts += [x, -h, z,  nx, 0.0, nz]
            verts += [x,  h, z,  nx, 0.0, nz]

        base_center = len(verts) // 6
        verts += [0.0, -h, 0.0,  0.0, -1.0, 0.0]
        top_center = len(verts) // 6
        verts += [0.0,  h, 0.0,  0.0,  1.0, 0.0]

        for i in range(self.sides):
            b0 = i * 2
            b1 = ((i + 1) % self.sides) * 2
            t0 = b0 + 1
            t1 = b1 + 1
            idxs += [b0, b1, t1,  b0, t1, t0]

        for i in range(self.sides):
            b0 = i * 2
            b1 = ((i + 1) % self.sides) * 2
            idxs += [base_center, b1, b0]
            idxs += [top_center, b0 + 1, b1 + 1]

        v = np.array(verts,  dtype=np.float32)
        i = np.array(idxs,   dtype=np.uint32)
        self._upload(v, i)
