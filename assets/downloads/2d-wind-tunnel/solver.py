import numpy as np

try:
    from numba import njit

    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    njit = None


AIRCRAFT_SPECS = {
    "B-2 Spirit": {
        "length": 8.8,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.06, 0.09, -0.08),
            (0.18, 0.16, -0.13),
            (0.38, 0.20, -0.16),
            (0.62, 0.18, -0.16),
            (0.82, 0.11, -0.12),
            (1.00, 0.02, -0.04),
        ],
        "polygons": [
            [(0.18, 0.00), (0.50, 0.32), (0.88, 0.05), (0.55, -0.12)],
            [(0.18, 0.00), (0.50, -0.32), (0.88, -0.05), (0.55, 0.12)],
        ],
        "ellipses": [],
    },
    "F-22 Raptor": {
        "length": 8.0,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.10, 0.08, -0.07),
            (0.24, 0.18, -0.12),
            (0.40, 0.18, -0.15),
            (0.68, 0.16, -0.15),
            (0.88, 0.11, -0.12),
            (1.00, 0.06, -0.07),
        ],
        "polygons": [
            [(0.35, -0.02), (0.68, -0.44), (0.56, -0.08)],
            [(0.68, -0.03), (0.94, -0.28), (0.82, -0.05)],
            [(0.76, 0.12), (0.93, 0.60), (0.86, 0.10)],
            [(0.83, 0.10), (0.99, 0.48), (0.94, 0.08)],
            [(0.28, 0.16), (0.43, 0.31), (0.51, 0.17)],
        ],
        "ellipses": [(0.38, 0.20, 0.09, 0.05)],
    },
    "F-15 Eagle": {
        "length": 8.2,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.12, 0.09, -0.08),
            (0.26, 0.18, -0.12),
            (0.48, 0.18, -0.15),
            (0.76, 0.16, -0.16),
            (0.94, 0.12, -0.13),
            (1.00, 0.10, -0.11),
        ],
        "polygons": [
            [(0.36, -0.02), (0.66, -0.40), (0.60, -0.08)],
            [(0.70, -0.04), (0.96, -0.24), (0.87, -0.06)],
            [(0.76, 0.12), (0.88, 0.62), (0.83, 0.11)],
            [(0.86, 0.11), (0.99, 0.58), (0.94, 0.10)],
            [(0.30, 0.16), (0.44, 0.30), (0.52, 0.17)],
        ],
        "ellipses": [(0.39, 0.21, 0.10, 0.05)],
    },
    "Boeing 777": {
        "length": 10.4,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.06, 0.14, -0.13),
            (0.16, 0.21, -0.20),
            (0.74, 0.22, -0.22),
            (0.88, 0.18, -0.18),
            (0.96, 0.10, -0.10),
            (1.00, 0.03, -0.03),
        ],
        "polygons": [
            [(0.42, -0.05), (0.71, -0.48), (0.60, -0.08)],
            [(0.78, 0.14), (0.93, 0.70), (0.88, 0.13)],
            [(0.81, 0.08), (1.00, 0.28), (0.92, 0.06)],
        ],
        "ellipses": [
            (0.53, -0.44, 0.08, 0.08),
            (0.66, -0.40, 0.07, 0.07),
            (0.10, 0.17, 0.06, 0.04),
        ],
    },
    "Airbus A350": {
        "length": 10.0,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.07, 0.13, -0.13),
            (0.17, 0.20, -0.20),
            (0.72, 0.21, -0.21),
            (0.87, 0.18, -0.18),
            (0.96, 0.09, -0.09),
            (1.00, 0.02, -0.03),
        ],
        "polygons": [
            [(0.42, -0.04), (0.73, -0.50), (0.60, -0.08)],
            [(0.78, 0.13), (0.92, 0.64), (0.87, 0.12)],
            [(0.80, 0.07), (1.00, 0.24), (0.91, 0.06)],
        ],
        "ellipses": [
            (0.54, -0.42, 0.075, 0.075),
            (0.66, -0.39, 0.065, 0.065),
            (0.10, 0.16, 0.055, 0.035),
        ],
    },
    "Cessna 172": {
        "length": 6.1,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.10, 0.12, -0.10),
            (0.24, 0.18, -0.17),
            (0.50, 0.19, -0.18),
            (0.76, 0.16, -0.14),
            (0.95, 0.08, -0.08),
            (1.00, 0.03, -0.03),
        ],
        "polygons": [
            [(0.26, 0.25), (0.65, 0.28), (0.52, 0.43), (0.18, 0.39)],
            [(0.75, 0.10), (0.93, 0.48), (0.86, 0.09)],
            [(0.76, 0.04), (0.99, 0.20), (0.88, 0.03)],
            [(0.26, 0.18), (0.45, 0.37), (0.55, 0.18)],
        ],
        "ellipses": [(0.34, 0.22, 0.12, 0.07), (0.18, -0.22, 0.035, 0.035)],
    },
    "Gulfstream G650": {
        "length": 8.5,
        "profile": [
            (0.00, 0.00, 0.00),
            (0.08, 0.11, -0.10),
            (0.20, 0.17, -0.17),
            (0.72, 0.17, -0.18),
            (0.86, 0.14, -0.14),
            (0.96, 0.08, -0.08),
            (1.00, 0.03, -0.03),
        ],
        "polygons": [
            [(0.45, -0.04), (0.68, -0.36), (0.58, -0.07)],
            [(0.79, 0.11), (0.93, 0.58), (0.87, 0.10)],
            [(0.80, 0.04), (0.99, 0.20), (0.90, 0.03)],
        ],
        "ellipses": [(0.80, -0.20, 0.055, 0.055), (0.09, 0.13, 0.05, 0.03)],
    },
}


# The selectable bodies are airfoil sections rather than aircraft silhouettes.
# Values use NACA-style camber and thickness ratios, expressed relative to chord.
AIRFOIL_SPECS = {
    "NACA 0012": {"camber": 0.00, "camber_position": 0.0, "thickness": 0.12},
    "NACA 2412": {"camber": 0.02, "camber_position": 0.4, "thickness": 0.12},
    "NACA 4412": {"camber": 0.04, "camber_position": 0.4, "thickness": 0.12},
    "NACA 23012": {"camber": 0.02, "camber_position": 0.3, "thickness": 0.12},
    "NACA 0018": {"camber": 0.00, "camber_position": 0.0, "thickness": 0.18},
    "NACA 6409": {"camber": 0.06, "camber_position": 0.4, "thickness": 0.09},
    "NACA 6418": {
        "camber": 0.06,
        "camber_position": 0.4,
        "thickness": 0.18,
    },
}


if NUMBA_AVAILABLE:

    @njit(cache=True)
    def _step_numba(f, scratch, rho, ux, uy, obstacle, u0, tau, num_steps):
        ny, nx, _ = f.shape
        omega = 1.0 / tau

        cxs = (0, 1, 0, -1, 0, 1, -1, -1, 1)
        cys = (0, 0, 1, 0, -1, 1, 1, -1, -1)
        weights = (
            4.0 / 9.0,
            1.0 / 9.0,
            1.0 / 9.0,
            1.0 / 9.0,
            1.0 / 9.0,
            1.0 / 36.0,
            1.0 / 36.0,
            1.0 / 36.0,
            1.0 / 36.0,
        )

        for _ in range(num_steps):
            for y in range(ny):
                for x in range(nx):
                    scratch[y, x, 0] = f[y, x, 0]
                    scratch[y, x, 1] = f[y, (x - 1) % nx, 1]
                    scratch[y, x, 2] = f[(y - 1) % ny, x, 2]
                    scratch[y, x, 3] = f[y, (x + 1) % nx, 3]
                    scratch[y, x, 4] = f[(y + 1) % ny, x, 4]
                    scratch[y, x, 5] = f[(y - 1) % ny, (x - 1) % nx, 5]
                    scratch[y, x, 6] = f[(y - 1) % ny, (x + 1) % nx, 6]
                    scratch[y, x, 7] = f[(y + 1) % ny, (x + 1) % nx, 7]
                    scratch[y, x, 8] = f[(y + 1) % ny, (x - 1) % nx, 8]

            for y in range(ny):
                for x in range(nx):
                    if obstacle[y, x]:
                        old1 = scratch[y, x, 1]
                        old2 = scratch[y, x, 2]
                        old5 = scratch[y, x, 5]
                        old6 = scratch[y, x, 6]

                        scratch[y, x, 1] = scratch[y, x, 3]
                        scratch[y, x, 2] = scratch[y, x, 4]
                        scratch[y, x, 3] = old1
                        scratch[y, x, 4] = old2
                        scratch[y, x, 5] = scratch[y, x, 7]
                        scratch[y, x, 6] = scratch[y, x, 8]
                        scratch[y, x, 7] = old5
                        scratch[y, x, 8] = old6

            for y in range(ny):
                for x in range(nx):
                    r = 0.0
                    for i in range(9):
                        r += scratch[y, x, i]

                    if r <= 0.0:
                        r = 1e-12

                    rho[y, x] = r
                    ux[y, x] = (
                        scratch[y, x, 1]
                        - scratch[y, x, 3]
                        + scratch[y, x, 5]
                        - scratch[y, x, 6]
                        - scratch[y, x, 7]
                        + scratch[y, x, 8]
                    ) / r
                    uy[y, x] = (
                        scratch[y, x, 2]
                        - scratch[y, x, 4]
                        + scratch[y, x, 5]
                        + scratch[y, x, 6]
                        - scratch[y, x, 7]
                        - scratch[y, x, 8]
                    ) / r

            for y in range(ny):
                ux[y, 0] = u0
                uy[y, 0] = 0.0
                rho[y, 0] = 1.0

                ux[y, nx - 1] = ux[y, nx - 2]
                uy[y, nx - 1] = uy[y, nx - 2]
                rho[y, nx - 1] = rho[y, nx - 2]

            # Open far-field treatment above and below the test article.
            # Copying the adjacent interior state gives a zero-normal-gradient
            # boundary, avoiding the artificial inlet-state reset that used to
            # imprint horizontal bands into the simulation.
            for x in range(1, nx - 1):
                ux[0, x] = ux[1, x]
                uy[0, x] = uy[1, x]
                rho[0, x] = rho[1, x]

                ux[ny - 1, x] = ux[ny - 2, x]
                uy[ny - 1, x] = uy[ny - 2, x]
                rho[ny - 1, x] = rho[ny - 2, x]

            for y in range(ny):
                for x in (0, nx - 1):
                    u_sq = ux[y, x] * ux[y, x] + uy[y, x] * uy[y, x]
                    for i in range(9):
                        cu = 3.0 * (cxs[i] * ux[y, x] + cys[i] * uy[y, x])
                        scratch[y, x, i] = rho[y, x] * weights[i] * (
                            1.0 + cu + 0.5 * cu * cu - 1.5 * u_sq
                        )

            for x in range(1, nx - 1):
                for y in (0, ny - 1):
                    u_sq = ux[y, x] * ux[y, x] + uy[y, x] * uy[y, x]
                    for i in range(9):
                        cu = 3.0 * (cxs[i] * ux[y, x] + cys[i] * uy[y, x])
                        scratch[y, x, i] = rho[y, x] * weights[i] * (
                            1.0 + cu + 0.5 * cu * cu - 1.5 * u_sq
                        )

            for y in range(ny):
                for x in range(nx):
                    u_sq = ux[y, x] * ux[y, x] + uy[y, x] * uy[y, x]
                    for i in range(9):
                        cu = 3.0 * (cxs[i] * ux[y, x] + cys[i] * uy[y, x])
                        feq = rho[y, x] * weights[i] * (
                            1.0 + cu + 0.5 * cu * cu - 1.5 * u_sq
                        )
                        f[y, x, i] = scratch[y, x, i] - omega * (
                            scratch[y, x, i] - feq
                        )


class LBMSolver:
    def __init__(
        self,
        nx=500,
        ny=220,
        u0=0.08,
        object_type="NACA 2412",
        angle_deg=0,
        obstacle_radius=18,
        object_detail=3,
        tau=0.6,
    ):
        self.nx = nx
        self.ny = ny
        self.u0 = u0
        self.tau = tau

        self.object_type = object_type
        self.angle_deg = angle_deg
        self.obstacle_radius = obstacle_radius
        self.object_detail = max(1, int(object_detail))

        self.cxs = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1], dtype=np.int8)
        self.cys = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1], dtype=np.int8)
        self.weights = np.array(
            [4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 36, 1 / 36, 1 / 36, 1 / 36]
        )

        self.rho = np.ones((ny, nx))
        self.ux = np.ones((ny, nx)) * u0
        self.uy = np.zeros((ny, nx))

        self.f = np.empty((ny, nx, 9))
        self.feq = np.empty_like(self.f)
        self.equilibrium(self.rho, self.ux, self.uy, out=self.f)

        self.obstacle_x = int(nx * 0.30)
        self.obstacle_y = ny // 2

        self.obstacle = self.create_obstacle_mask()

    def rotate_coordinates(self, X, Y, angle_deg):
        angle = np.deg2rad(angle_deg)

        x = X - self.obstacle_x
        y = Y - self.obstacle_y

        x_rot = x * np.cos(angle) + y * np.sin(angle)
        y_rot = -x * np.sin(angle) + y * np.cos(angle)

        return x_rot, y_rot

    def create_obstacle_mask(self):
        if self.object_detail <= 1:
            return self.create_obstacle_mask_at_resolution(self.nx, self.ny)

        ss = self.object_detail
        mask = self.create_obstacle_mask_at_resolution(self.nx * ss, self.ny * ss, ss)
        coverage = mask.reshape(self.ny, ss, self.nx, ss).mean(axis=(1, 3))
        return coverage >= 0.28

    def create_obstacle_mask_at_resolution(self, nx, ny, scale=1):
        x = np.arange(nx)
        y = np.arange(ny)
        if scale != 1:
            x = (np.arange(nx) + 0.5) / scale - 0.5
            y = (np.arange(ny) + 0.5) / scale - 0.5

        X, Y = np.meshgrid(x, y)

        x_rot, y_rot = self.rotate_coordinates(X, Y, self.angle_deg)

        if self.object_type == "Golfball":
            return self.create_golfball_mask(x_rot, y_rot)

        if self.object_type == "Circular cylinder":
            return self.create_cylinder_mask(x_rot, y_rot)

        if self.object_type == "Flat rectangle":
            return self.create_rectangle_mask(x_rot, y_rot)

        if self.object_type == "Square block":
            return self.create_square_mask(x_rot, y_rot)

        if self.object_type == "Ellipse":
            return self.create_ellipse_mask(x_rot, y_rot)

        if self.object_type == "Triangle wedge":
            return self.create_triangle_mask(x_rot, y_rot)

        if self.object_type == "Two cylinders":
            return self.create_two_cylinders_mask(x_rot, y_rot)

        if self.object_type == "Double-wedge supersonic":
            return self.create_double_wedge_airfoil_mask(x_rot, y_rot)

        if self.object_type in AIRFOIL_SPECS:
            return self.create_naca_airfoil_mask(
                x_rot, y_rot, AIRFOIL_SPECS[self.object_type]
            )

        return self.create_naca_airfoil_mask(x_rot, y_rot, AIRFOIL_SPECS["NACA 2412"])

    def create_cylinder_mask(self, x_rot, y_rot):
        return x_rot**2 + y_rot**2 < self.obstacle_radius**2

    def create_golfball_mask(self, x_rot, y_rot):
        r = np.sqrt(x_rot**2 + y_rot**2)
        theta = np.arctan2(y_rot, x_rot)

        base_radius = self.obstacle_radius
        dimple_count = 18
        dimple_depth = 0.055

        local_radius = base_radius * (
            1
            - dimple_depth * np.cos(dimple_count * theta)
            - 0.018 * np.cos(2 * dimple_count * theta)
        )

        return r < local_radius

    def create_rectangle_mask(self, x_rot, y_rot):
        length = self.obstacle_radius * 5.5
        thickness = self.obstacle_radius * 0.55

        return (np.abs(x_rot) < length / 2) & (np.abs(y_rot) < thickness / 2)

    def create_square_mask(self, x_rot, y_rot):
        half_width = self.obstacle_radius * 1.15
        return (np.abs(x_rot) < half_width) & (np.abs(y_rot) < half_width)

    def create_ellipse_mask(self, x_rot, y_rot):
        length = self.obstacle_radius * 2.4
        thickness = self.obstacle_radius * 0.9
        return (x_rot / length) ** 2 + (y_rot / thickness) ** 2 < 1

    def create_triangle_mask(self, x_rot, y_rot):
        length = self.obstacle_radius * 3.4
        half_height = self.obstacle_radius * 1.25
        x = x_rot + length / 2
        valid_x = (x >= 0) & (x <= length)
        local_half_height = half_height * (1 - x / length)
        return valid_x & (np.abs(y_rot) <= local_half_height)

    def create_two_cylinders_mask(self, x_rot, y_rot):
        radius = self.obstacle_radius * 0.75
        spacing = self.obstacle_radius * 2.4
        front = (x_rot + spacing / 2) ** 2 + y_rot**2 < radius**2
        rear = (x_rot - spacing / 2) ** 2 + y_rot**2 < radius**2
        return front | rear

    def polygon_mask(self, x_rot, y_rot, points):
        inside = np.zeros_like(x_rot, dtype=bool)
        count = len(points)

        for i in range(count):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % count]
            crosses = (y1 > y_rot) != (y2 > y_rot)
            x_at_y = (x2 - x1) * (y_rot - y1) / (y2 - y1 + 1e-12) + x1
            inside ^= crosses & (x_rot < x_at_y)

        return inside

    def create_aircraft_side_mask(self, x_rot, y_rot, spec):
        length = self.obstacle_radius * spec["length"]
        height = self.obstacle_radius
        x = x_rot + length / 2
        x_norm = x / length
        profile = np.array(spec["profile"], dtype=float)
        top = np.interp(x_norm, profile[:, 0], profile[:, 1])
        bottom = np.interp(x_norm, profile[:, 0], profile[:, 2])
        mask = (x_norm >= 0) & (x_norm <= 1) & (y_rot <= top * height) & (
            y_rot >= bottom * height
        )

        for polygon in spec["polygons"]:
            points = [((px - 0.5) * length, py * height) for px, py in polygon]
            mask |= self.polygon_mask(x_rot, y_rot, points)

        for ex, ey, ew, eh in spec["ellipses"]:
            cx = (ex - 0.5) * length
            cy = ey * height
            rx = max(1.0, ew * length)
            ry = max(1.0, eh * height)
            mask |= ((x_rot - cx) / rx) ** 2 + ((y_rot - cy) / ry) ** 2 < 1

        return mask

    def create_naca_airfoil_mask(self, x_rot, y_rot, spec):
        """Create a four-digit NACA-style airfoil from camber/thickness ratios."""
        chord = self.obstacle_radius * 7.5
        thickness_ratio = spec["thickness"]
        camber = spec["camber"]
        camber_position = spec["camber_position"]

        x = x_rot + chord / 2
        valid_x = (x >= 0) & (x <= chord)

        x_norm = np.zeros_like(x, dtype=float)
        x_norm[valid_x] = x[valid_x] / chord

        yt = 5 * thickness_ratio * chord * (
            0.2969 * np.sqrt(np.maximum(x_norm, 0))
            - 0.1260 * x_norm
            - 0.3516 * x_norm**2
            + 0.2843 * x_norm**3
            - 0.1015 * x_norm**4
        )

        if camber == 0:
            yc = np.zeros_like(x_norm)
        else:
            yc = np.where(
                x_norm < camber_position,
                camber
                * chord
                / camber_position**2
                * (2 * camber_position * x_norm - x_norm**2),
                camber
                * chord
                / (1 - camber_position) ** 2
                * (
                    (1 - 2 * camber_position)
                    + 2 * camber_position * x_norm
                    - x_norm**2
                ),
            )

        upper = yc + yt
        lower = yc - yt

        return valid_x & (y_rot <= upper) & (y_rot >= lower)

    def create_double_wedge_airfoil_mask(self, x_rot, y_rot):
        """Thin, sharp double-wedge section for supersonic-flow demonstrations."""
        chord = self.obstacle_radius * 8.5
        x = x_rot + chord / 2
        x_norm = x / chord
        valid_x = (x_norm >= 0) & (x_norm <= 1)
        half_thickness = 0.06 * chord * (1 - np.abs(2 * x_norm - 1))
        return valid_x & (np.abs(y_rot) <= half_thickness)

    def set_angle_of_attack(self, angle_deg):
        """
        Update AoA while running.

        This is a simplified moving-boundary method.
        It is useful for live visualization, but not fully physically exact.
        """
        if angle_deg == self.angle_deg:
            return

        old_obstacle = self.obstacle.copy()

        self.angle_deg = angle_deg
        new_obstacle = self.create_obstacle_mask()

        newly_fluid = old_obstacle & ~new_obstacle
        newly_solid = new_obstacle & ~old_obstacle

        self.obstacle = new_obstacle

        self.rho[newly_fluid] = 1.0
        self.ux[newly_fluid] = self.u0
        self.uy[newly_fluid] = 0.0

        self.rho[newly_solid] = 1.0
        self.ux[newly_solid] = 0.0
        self.uy[newly_solid] = 0.0

        self.equilibrium(self.rho, self.ux, self.uy, out=self.feq)

        self.f[newly_fluid, :] = self.feq[newly_fluid, :]
        self.f[newly_solid, :] = self.feq[newly_solid, :]

    def equilibrium(self, rho, ux, uy, out=None):
        if out is None:
            out = np.empty(rho.shape + (9,))

        u_sq = ux**2 + uy**2

        for i, cx, cy, w in zip(range(9), self.cxs, self.cys, self.weights):
            cu = 3 * (cx * ux + cy * uy)
            out[..., i] = rho * w * (1 + cu + 0.5 * cu**2 - 1.5 * u_sq)

        return out

    def apply_far_field_boundaries(self):
        self.ux[:, 0] = self.u0
        self.uy[:, 0] = 0
        self.rho[:, 0] = 1.0

        self.ux[:, -1] = self.ux[:, -2]
        self.uy[:, -1] = self.uy[:, -2]
        self.rho[:, -1] = self.rho[:, -2]

        # Open far-field boundaries: extrapolate the adjacent interior state
        # instead of repeatedly forcing the inlet state across the top/bottom.
        self.ux[0, 1:-1] = self.ux[1, 1:-1]
        self.uy[0, 1:-1] = self.uy[1, 1:-1]
        self.rho[0, 1:-1] = self.rho[1, 1:-1]

        self.ux[-1, 1:-1] = self.ux[-2, 1:-1]
        self.uy[-1, 1:-1] = self.uy[-2, 1:-1]
        self.rho[-1, 1:-1] = self.rho[-2, 1:-1]

        self.f[:, 0, :] = self.equilibrium(
            self.rho[:, 0], self.ux[:, 0], self.uy[:, 0]
        )
        self.f[:, -1, :] = self.equilibrium(
            self.rho[:, -1], self.ux[:, -1], self.uy[:, -1]
        )
        self.f[0, 1:-1, :] = self.equilibrium(
            self.rho[0, 1:-1], self.ux[0, 1:-1], self.uy[0, 1:-1]
        )
        self.f[-1, 1:-1, :] = self.equilibrium(
            self.rho[-1, 1:-1], self.ux[-1, 1:-1], self.uy[-1, 1:-1]
        )

    def step(self, num_steps=10):
        if NUMBA_AVAILABLE:
            _step_numba(
                self.f,
                self.feq,
                self.rho,
                self.ux,
                self.uy,
                self.obstacle,
                self.u0,
                self.tau,
                num_steps,
            )
            return

        for _ in range(num_steps):
            for i, cx, cy in zip(range(9), self.cxs, self.cys):
                self.f[:, :, i] = np.roll(self.f[:, :, i], cx, axis=1)
                self.f[:, :, i] = np.roll(self.f[:, :, i], cy, axis=0)

            bndry_f = self.f[self.obstacle, :].copy()

            self.f[self.obstacle, 1] = bndry_f[:, 3]
            self.f[self.obstacle, 2] = bndry_f[:, 4]
            self.f[self.obstacle, 3] = bndry_f[:, 1]
            self.f[self.obstacle, 4] = bndry_f[:, 2]
            self.f[self.obstacle, 5] = bndry_f[:, 7]
            self.f[self.obstacle, 6] = bndry_f[:, 8]
            self.f[self.obstacle, 7] = bndry_f[:, 5]
            self.f[self.obstacle, 8] = bndry_f[:, 6]

            np.sum(self.f, axis=2, out=self.rho)
            np.maximum(self.rho, 1e-12, out=self.rho)

            self.ux[:, :] = (
                self.f[:, :, 1]
                - self.f[:, :, 3]
                + self.f[:, :, 5]
                - self.f[:, :, 6]
                - self.f[:, :, 7]
                + self.f[:, :, 8]
            ) / self.rho
            self.uy[:, :] = (
                self.f[:, :, 2]
                - self.f[:, :, 4]
                + self.f[:, :, 5]
                + self.f[:, :, 6]
                - self.f[:, :, 7]
                - self.f[:, :, 8]
            ) / self.rho

            self.apply_far_field_boundaries()

            self.equilibrium(self.rho, self.ux, self.uy, out=self.feq)
            self.f += -(1 / self.tau) * (self.f - self.feq)

    def get_velocity_magnitude(self):
        velocity = np.sqrt(self.ux**2 + self.uy**2)
        velocity[self.obstacle] = np.nan
        return velocity

    def get_vorticity(self):
        dudy = np.gradient(self.ux, axis=0)
        dvdx = np.gradient(self.uy, axis=1)
        vort = dvdx - dudy
        vort[self.obstacle] = np.nan
        return vort

    def get_obstacle_mask(self):
        return self.obstacle
