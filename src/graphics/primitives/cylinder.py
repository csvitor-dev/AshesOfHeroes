import numpy as np
import math
from src.graphics.primitives.entity_3d import Entity3D


class Cylinder(Entity3D):

    def __init__(self, radius: float = 0.3, height: float = 0.2, segments: int = 24):
        super().__init__()
        self.radius = radius
        self.height = height
        self.segments = segments
        self._build_geometry()

    def _build_geometry(self):
        verts: list[float] = []
        idxs: list[int] = []
        step = 2 * math.pi / self.segments
        h = self.height / 2

        for i in range(self.segments):
            a = i * step
            x = math.cos(a) * self.radius
            z = math.sin(a) * self.radius
            nx = math.cos(a + step / 2)
            nz = math.sin(a + step / 2)

            verts += [x, -h, z,  nx, 0.0, nz]
            verts += [x,  h, z,  nx, 0.0, nz]

        bc = len(verts) // 6
        verts += [0.0, -h, 0.0,  0.0, -1.0, 0.0]
        tc = len(verts) // 6
        verts += [0.0,  h, 0.0,  0.0,  1.0, 0.0]

        for i in range(self.segments):
            b0, b1 = i * 2, ((i + 1) % self.segments) * 2
            t0, t1 = b0 + 1, b1 + 1
            idxs += [b0, b1, t1,  b0, t1, t0]
            idxs += [bc, b1, b0]
            idxs += [tc, b0 + 1, b1 + 1]

        self._upload(
            np.array(verts, dtype=np.float32),
            np.array(idxs,  dtype=np.uint32),
        )
