import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class MyceliumObservatoryVisual(VisualBase):
    """Bioluminescent fungal lattice grown via reaction-diffusion dynamics."""

    metadata = {
        "name": "Mycelium Observatory",
        "author": "sat",
        "version": "1.2",
        "description": "Procedural micelio vivo con bioluminiscencia y ramas inteligentes",
        "ai_creator": "gpt-5-codex",
    }

    def __init__(self):
        random.seed(1337)
        self.prev_size = (0, 0)
        self.u_field = []
        self.v_field = []
        self.rd_buffer_u = []
        self.rd_buffer_v = []
        self.glow = []
        self.branches = []
        self.frame_count = 0
        self.char_ramp = [" ", ".", "·", "*", "o", "0", "#", "▒", "▓", "█"]
        self.branch_limit = 22
        self.aspect = 1.8  # compensate terminal cell proportions
        self.wave_x = []
        self.wave_y = []
        self.col_wave_x = []
        self.col_wave_y = []
        self.vein = []
        self.ortho_weight = 0.5
        self.diag_weight = 0.2
        self.center_weight = self.ortho_weight * 4 + self.diag_weight * 4
        self.spore_interval = 120

        # Gray-Scott parameters
        self.Du = 0.16
        self.Dv = 0.08
        self.feed = 0.035
        self.kill = 0.062
        self.dt = 1.0

    def _ensure_state(self, width, height):
        if (width, height) == self.prev_size:
            return

        self.prev_size = (width, height)
        total = width * height

        self.u_field = [1.0 for _ in range(total)]
        self.v_field = [0.0 for _ in range(total)]
        self.rd_buffer_u = [0.0 for _ in range(total)]
        self.rd_buffer_v = [0.0 for _ in range(total)]
        self.glow = [0.0 for _ in range(total)]
        self.branches = []
        self.vein = [0.0 for _ in range(total)]
        self.frame_count = 0
        self.wave_x = [(random.random() - 0.5) * 2.0 + x * 0.12 for x in range(width)]
        self.wave_y = [(random.random() - 0.5) * 2.0 + y * 0.17 for y in range(height)]
        self.col_wave_x = [math.sin(x * 0.11) for x in range(width)]
        self.col_wave_y = [math.cos(y * 0.09) for y in range(height)]

        # Seed initial nutrient patches
        for _ in range(12):
            self._seed_spot(width, height)

        # Spawn initial branches near seeded zones
        for _ in range(12):
            self._spawn_branch(width, height)

    def _index(self, width, x, y):
        return y * width + x

    def _seed_spot(self, width, height):
        cx = random.randint(int(width * 0.2), int(width * 0.8))
        cy = random.randint(int(height * 0.2), int(height * 0.8))
        radius = random.randint(2, max(3, min(width, height) // 8))
        for y in range(max(0, cy - radius), min(height, cy + radius)):
            for x in range(max(0, cx - radius), min(width, cx + radius)):
                dx = x - cx
                dy = y - cy
                if dx * dx + dy * dy <= radius * radius:
                    idx = self._index(width, x, y)
                    self.v_field[idx] = min(1.0, self.v_field[idx] + random.uniform(0.2, 0.6))
                    self.u_field[idx] = max(0.2, self.u_field[idx] - random.uniform(0.05, 0.1))

    def _spawn_branch(self, width, height):
        if len(self.branches) >= self.branch_limit:
            return

        x = random.uniform(0, width - 1)
        y = random.uniform(0, height - 1)
        angle = random.uniform(0, math.tau)
        branch = {
            "x": x,
            "y": y,
            "dx": math.cos(angle),
            "dy": math.sin(angle) / self.aspect,
            "age": 0,
            "burst": random.uniform(0.12, 0.35),
        }
        self.branches.append(branch)

    def _deposit_energy(self, width, height, x, y, glow_amt, trail_amt):
        ix = int(x)
        iy = int(y)
        if 0 <= ix < width and 0 <= iy < height:
            idx = self._index(width, ix, iy)
            if glow_amt:
                self.glow[idx] = min(2.0, self.glow[idx] + glow_amt)
            if trail_amt:
                self.vein[idx] = min(1.6, self.vein[idx] + trail_amt)

    def _enrich_patch(self, width, height, x, y, radius, intensity):
        if width == 0 or height == 0:
            return

        cx = int(x) % width
        cy = int(y) % height
        w = width
        v_field = self.v_field
        u_field = self.u_field
        for dy in range(-radius, radius + 1):
            yy = (cy + dy) % height
            row = yy * w
            abs_dy = abs(dy)
            for dx in range(-radius, radius + 1):
                if abs(dx) + abs_dy > radius:
                    continue
                xx = (cx + dx) % width
                idx = row + xx
                falloff = 1.0 - (abs(dx) + abs_dy) / (radius + 1.0)
                boost = intensity * falloff
                v_field[idx] = min(1.3, v_field[idx] + 0.09 * boost)
                u_field[idx] = max(0.0, u_field[idx] - 0.04 * boost)
                self.vein[idx] = min(1.4, self.vein[idx] + 0.05 * boost)

    def _advance_branches(self, width, height, time_offset):
        if not self.branches:
            return

        gradient_scale = 0.55
        step = 0.6

        for branch in list(self.branches):
            gx = self._sample_gradient(self.v_field, width, height, branch["x"], branch["y"], axis=0)
            gy = self._sample_gradient(self.v_field, width, height, branch["x"], branch["y"], axis=1)

            branch["dx"] = branch["dx"] * 0.65 + gradient_scale * gx + random.uniform(-0.1, 0.1)
            branch["dy"] = branch["dy"] * 0.65 + gradient_scale * gy + random.uniform(-0.08, 0.08)

            norm = math.hypot(branch["dx"], branch["dy"] * self.aspect)
            if norm > 1e-5:
                branch["dx"] /= norm
                branch["dy"] /= norm

            branch["x"] = (branch["x"] + branch["dx"] * step) % max(width, 1)
            branch["y"] = (branch["y"] + branch["dy"] * step * self.aspect) % max(height, 1)
            branch["age"] += 1

            self._deposit_energy(
                width,
                height,
                branch["x"],
                branch["y"],
                0.18 + branch["burst"] * 0.55,
                0.26 + branch["burst"] * 0.4,
            )
            self._deposit_energy(
                width,
                height,
                branch["x"] - branch["dx"] * 0.45,
                branch["y"] - branch["dy"] * 0.45,
                0.05,
                0.12,
            )
            if random.random() < 0.08:
                self._deposit_energy(
                    width,
                    height,
                    branch["x"] + branch["dy"] * 0.6,
                    branch["y"] - branch["dx"] * 0.6,
                    0.07,
                    0.18,
                )

            if branch["age"] % 7 == 0:
                idx = self._index(width, int(branch["x"]), int(branch["y"]))
                self.v_field[idx] = min(1.2, self.v_field[idx] + 0.08 * branch["burst"])
                self.u_field[idx] = max(0.0, self.u_field[idx] - 0.04 * branch["burst"])
            if branch["age"] % 45 == 0:
                self._enrich_patch(width, height, branch["x"], branch["y"], 3, 0.8 + branch["burst"])

            if branch["age"] > 450:
                self.branches.remove(branch)
                self._spawn_branch(width, height)
                continue

            # Branch splitting
            if (
                branch["age"] > 120
                and len(self.branches) < self.branch_limit
                and random.random() < 0.02
            ):
                child = {
                    "x": branch["x"],
                    "y": branch["y"],
                    "dx": branch["dy"],
                    "dy": -branch["dx"],
                    "age": 0,
                    "burst": random.uniform(0.1, 0.28),
                }
                self.branches.append(child)

    def _sample_gradient(self, field, width, height, fx, fy, axis=0):
        if width == 0 or height == 0:
            return 0.0

        ix = int(fx) % width
        iy = int(fy) % height
        row = iy * width

        if axis == 0:
            left = field[row + (ix - 1) % width]
            right = field[row + (ix + 1) % width]
            return (right - left) * 0.5
        else:
            up = field[((iy - 1) % height) * width + ix]
            down = field[((iy + 1) % height) * width + ix]
            return (down - up) * 0.5

    def _spore_burst(self, width, height):
        if not self.branches or width == 0 or height == 0:
            return

        branch = random.choice(self.branches)
        cx = int(branch["x"]) % width
        cy = int(branch["y"]) % height
        radius = random.randint(2, max(3, min(width, height) // 5))
        glow = self.glow
        v_field = self.v_field
        u_field = self.u_field
        w = width

        for dy in range(-radius, radius + 1):
            yy = (cy + dy) % height
            row = yy * w
            for dx in range(-radius, radius + 1):
                dist_sq = dx * dx + dy * dy
                if dist_sq > radius * radius:
                    continue
                xx = (cx + dx) % width
                idx = row + xx
                falloff = 1.0 - (dist_sq ** 0.5) / (radius + 1.0)
                if falloff <= 0.0:
                    continue
                glow[idx] = min(1.8, glow[idx] + 0.7 * falloff)
                v_field[idx] = min(1.4, v_field[idx] + 0.18 * falloff)
                u_field[idx] = max(0.0, u_field[idx] - 0.07 * falloff)
                self.vein[idx] = min(1.6, self.vein[idx] + 0.12 * falloff)

    def _update_reaction_diffusion(self, width, height, time_offset):
        if width == 0 or height == 0:
            return

        Du = self.Du
        Dv = self.Dv
        dt = self.dt
        ortho = self.ortho_weight
        diag = self.diag_weight
        center = self.center_weight
        wave_x = self.wave_x
        wave_y = self.wave_y

        feed_base = self.feed + 0.005 * math.sin(time_offset * 0.05)
        kill_base = self.kill + 0.003 * math.cos(time_offset * 0.04)

        u = self.u_field
        v = self.v_field
        buf_u = self.rd_buffer_u
        buf_v = self.rd_buffer_v

        for iteration in range(2):
            phase_shift = time_offset * 0.07 + iteration * 0.9
            for y in range(height):
                y_up = y - 1 if y > 0 else height - 1
                y_down = y + 1 if y < height - 1 else 0
                row = y * width
                row_up = y_up * width
                row_down = y_down * width
                wave_y_val = wave_y[y]

                for x in range(width):
                    x_left = x - 1 if x > 0 else width - 1
                    x_right = x + 1 if x < width - 1 else 0
                    idx = row + x

                    u_c = u[idx]
                    v_c = v[idx]

                    ortho_u = (
                        u[row + x_left] + u[row + x_right] +
                        u[row_up + x] + u[row_down + x]
                    )
                    diag_u = (
                        u[row_up + x_left] + u[row_up + x_right] +
                        u[row_down + x_left] + u[row_down + x_right]
                    )
                    lap_u = ortho_u * ortho + diag_u * diag - u_c * center

                    ortho_v = (
                        v[row + x_left] + v[row + x_right] +
                        v[row_up + x] + v[row_down + x]
                    )
                    diag_v = (
                        v[row_up + x_left] + v[row_up + x_right] +
                        v[row_down + x_left] + v[row_down + x_right]
                    )
                    lap_v = ortho_v * ortho + diag_v * diag - v_c * center

                    wave_phase = phase_shift + wave_x[x] + wave_y_val
                    feed_local = feed_base + 0.006 * math.sin(wave_phase)
                    kill_local = kill_base + 0.004 * math.cos(wave_phase * 1.2)

                    uvv = u_c * v_c * v_c
                    du = Du * lap_u - uvv + feed_local * (1.0 - u_c)
                    dv = Dv * lap_v + uvv - (feed_local + kill_local) * v_c

                    buf_u[idx] = max(0.0, min(1.2, u_c + du * dt))
                    buf_v[idx] = max(0.0, min(1.2, v_c + dv * dt))

            u, buf_u = buf_u, u
            v, buf_v = buf_v, v

        self.u_field = u
        self.v_field = v
        self.rd_buffer_u = buf_u
        self.rd_buffer_v = buf_v

        # Occasional nutrient surge
        if self.frame_count % 90 == 10:
            self._seed_spot(width, height)

    def _hsv_to_rgb(self, h, s, v):
        h = h % 1.0
        s = max(0.0, min(1.0, s))
        v = max(0.0, min(1.0, v))
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        return int(r * 255), int(g * 255), int(b * 255)

    def _compose_frame(self, width, height, time_offset):
        pattern = []
        if width == 0 or height == 0:
            return pattern

        flicker = 0.55 + 0.45 * math.sin(time_offset * 0.33)
        swirl_phase = time_offset * 0.19
        hue_time = time_offset * 0.23
        spore_phase = time_offset * 0.52
        parallax_phase = time_offset * 0.17
        glow_decay = 0.92
        trail_decay = 0.955

        glow = self.glow
        u_field = self.u_field
        v_field = self.v_field
        vein = self.vein
        ramp = self.char_ramp
        ramp_max = len(ramp) - 1
        col_wave_x = self.col_wave_x
        col_wave_y = self.col_wave_y

        for y in range(height):
            row_chars = []
            wave_y_val = col_wave_y[y] if col_wave_y else 0.0
            row = y * width
            for x in range(width):
                idx = row + x
                gl = glow[idx] * glow_decay
                glow[idx] = gl
                trail = vein[idx] * trail_decay
                vein[idx] = trail
                u_val = u_field[idx]
                v_val = v_field[idx]

                wave_phase = swirl_phase + col_wave_x[x] + wave_y_val
                spore_wave = math.sin(spore_phase + x * 0.18 + wave_y_val * 1.7)
                spore_wave += 0.6 * math.cos(spore_phase * 0.8 + x * 0.07 - y * 0.11)
                spore = max(0.0, spore_wave) * (0.22 + 0.55 * (v_val + gl))

                lum = v_val - 0.33 * u_val + gl + 0.18 * trail + 0.18 * math.sin(wave_phase * 1.3)
                lum += 0.32 * spore
                lum = max(0.0, min(1.4, lum))
                lum = lum * (0.6 + lum * 0.4)
                lum_norm = max(0.0, min(1.0, lum))

                ramp_level = min(1.0, lum_norm + 0.35 * trail + 0.18 * spore)
                ramp_idx = int(ramp_level * ramp_max)
                ch = ramp[ramp_idx]

                depth = 0.5 + 0.5 * math.sin(
                    parallax_phase
                    + (x - width * 0.5) * 0.07
                    + (y - height * 0.5) * 0.05
                    + v_val * 0.9
                    - u_val * 0.6
                )
                depth = max(0.0, min(1.0, depth))

                hue = 0.56 + 0.22 * math.sin(hue_time + col_wave_x[x] * 1.8 + wave_y_val * 1.2)
                hue += 0.25 * (depth - 0.5) + 0.14 * ramp_level
                sat = 0.6 + 0.32 * ramp_level + 0.12 * max(0.0, spore_wave)
                val = 0.26 + 0.74 * (
                    lum_norm * flicker
                    + min(1.0, gl) * 0.35
                    + depth * 0.25
                    + trail * 0.28
                )

                r, g, b = self._hsv_to_rgb(hue, sat, val)
                color = rgb_to_ansi(r, g, b) if ramp_level > 0.05 else ""

                row_chars.append(color + ch if color else ch)

            pattern.append("".join(row_chars) + reset_color())

        return pattern

    def generate_frame(self, width, height, time_offset):
        self._ensure_state(width, height)
        self.frame_count += 1

        self._update_reaction_diffusion(width, height, time_offset)
        self._advance_branches(width, height, time_offset)
        if self.frame_count % self.spore_interval == 0:
            self._spore_burst(width, height)

        return self._compose_frame(width, height, time_offset)
