import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class EventHorizonVisual(VisualBase):
    """Ultra-detailed black hole with gravitational lensing"""

    metadata = {
        "name": "Event Horizon",
        "author": "sat",
        "version": "3.0",
        "description": "Supermassive black hole - gravitational lensing, accretion disk, spacetime distortion",
        "ai_creator": "Claude Opus 4.5"
    }

    def __init__(self):
        random.seed(2049)

        # More stars for lensing effect
        self.stars = []
        for _ in range(60):
            self.stars.append((
                random.random() * 2 - 1,
                random.random() * 2 - 1,
                0.3 + random.random() * 0.7,
                random.random() * 6.28,
                random.random() * 0.3,  # color tint
            ))

        # Pre-compute sin/cos lookup (128 entries for smoother curves)
        self.sin_table = [math.sin(i * 6.28 / 128) for i in range(128)]
        self.cos_table = [math.cos(i * 6.28 / 128) for i in range(128)]

        self.chars = " ·∙░▒▓▓█"

        # Black hole params
        self.rs = 0.08  # Schwarzschild radius
        self.photon_sphere = 0.12
        self.disk_inner = 0.14
        self.disk_outer = 0.65

    def _fast_sin(self, x):
        idx = int((x % 6.28) * 20.37) & 127
        return self.sin_table[idx]

    def _fast_cos(self, x):
        idx = int((x % 6.28) * 20.37) & 127
        return self.cos_table[idx]

    def _gravitational_lensing(self, nx, ny, r, rs):
        """Apply gravitational lensing distortion to coordinates"""
        if r < rs * 1.2:
            return nx, ny, 0  # Inside event horizon

        # Einstein ring effect - stronger near black hole
        deflection = rs * rs / (r * r) * 2.5

        # Radial distortion
        angle = math.atan2(ny, nx)
        new_r = r + deflection * (1.0 / r)

        # Tangential stretch (frame dragging simulation)
        angle_shift = deflection * 0.5

        lensed_x = new_r * self._fast_cos(angle + angle_shift)
        lensed_y = new_r * self._fast_sin(angle + angle_shift)

        return lensed_x, lensed_y, deflection

    def generate_frame(self, width, height, time_offset):
        t = time_offset
        cx, cy = width * 0.5, height * 0.5
        aspect = 2.0
        scale = min(width, height * aspect)
        inv_scale = 1.0 / scale

        rs = self.rs
        ps = self.photon_sphere
        disk_inner = self.disk_inner
        disk_outer = self.disk_outer

        # Pre-calculate time values
        t05 = t * 0.5
        t08 = t * 0.8
        t12 = t * 1.2
        t15 = t * 1.5
        t2 = t * 2
        t3 = t * 3
        t4 = t * 4

        output = []

        for y in range(height):
            row_chars = []
            row_colors = []

            ny_base = (y - cy) * aspect * inv_scale

            for x in range(width):
                nx = (x - cx) * inv_scale
                ny = ny_base

                r_sq = nx * nx + ny * ny
                r = math.sqrt(r_sq) if r_sq > 0.0001 else 0.01

                char = ' '
                color = None
                intensity = 0

                # === ABSOLUTE DARKNESS - EVENT HORIZON ===
                if r < rs:
                    row_chars.append(' ')
                    row_colors.append(None)
                    continue

                # Get lensed coordinates for background effects
                lensed_x, lensed_y, deflection = self._gravitational_lensing(nx, ny, r, rs)
                lensed_r = math.sqrt(lensed_x * lensed_x + lensed_y * lensed_y)

                # === EINSTEIN RING (bright ring at photon sphere) ===
                ps_dist = abs(r - ps)
                if ps_dist < rs * 0.35:
                    ring_int = 1.0 - ps_dist / (rs * 0.35)
                    ring_int = ring_int ** 1.5  # Sharper falloff

                    # Pulsing glow
                    pulse = 0.8 + 0.2 * self._fast_sin(t2 + r * 20)
                    ring_int *= pulse

                    if ring_int > intensity:
                        intensity = ring_int
                        idx = min(7, int(ring_int * 7))
                        char = self.chars[idx]
                        # Brilliant white-blue
                        c = int(200 + 55 * ring_int)
                        color = rgb_to_ansi(c, c, 255)

                # === INNER ACCRETION RING (hottest, brightest) ===
                inner_ring_r = disk_inner * 1.1
                inner_dist = abs(r - inner_ring_r)
                if inner_dist < rs * 0.4 and intensity < 0.9:
                    inner_int = 1.0 - inner_dist / (rs * 0.4)
                    # Extreme rotation effect
                    angle = math.atan2(ny, nx)
                    rotation = 0.6 + 0.4 * self._fast_sin(angle * 2 - t4)
                    inner_int *= rotation

                    if inner_int > intensity:
                        intensity = inner_int
                        idx = min(7, int(inner_int * 7))
                        char = self.chars[idx]
                        # White-hot
                        color = rgb_to_ansi(
                            int(255 * inner_int),
                            int(240 * inner_int),
                            int(200 * inner_int)
                        )

                # === MAIN ACCRETION DISK ===
                if disk_inner < r < disk_outer and intensity < 0.8:
                    # Disk with inclination (tilted view)
                    disk_y = ny * 1.4  # Perspective stretch
                    r_disk = math.sqrt(nx * nx + disk_y * disk_y)

                    if disk_inner < r_disk < disk_outer:
                        # Temperature gradient (hotter inside)
                        temp = 1.0 - (r_disk - disk_inner) / (disk_outer - disk_inner)
                        temp = temp ** 0.75  # More realistic T profile

                        disk_angle = math.atan2(disk_y, nx)

                        # Relativistic Doppler beaming
                        orbital_vel = 0.5 * math.sqrt(rs / r_disk)
                        doppler = 1.0 + orbital_vel * self._fast_sin(disk_angle)

                        # Spiral density waves
                        spiral1 = 0.6 + 0.4 * self._fast_sin(2 * disk_angle - r_disk * 12 + t15)
                        spiral2 = 0.7 + 0.3 * self._fast_sin(3 * disk_angle - r_disk * 8 + t12)

                        # Turbulence
                        turb = 0.85 + 0.15 * self._fast_sin(disk_angle * 7 + r_disk * 25 + t3)

                        disk_int = temp * doppler * spiral1 * spiral2 * turb
                        disk_int = max(0, min(1, disk_int))

                        if disk_int > intensity and disk_int > 0.1:
                            intensity = disk_int
                            idx = min(7, int(disk_int * 7))
                            char = self.chars[idx]

                            # Color based on temperature and Doppler
                            if temp > 0.75:
                                # Inner - white/blue
                                cr = int(255 * disk_int)
                                cg = int(250 * disk_int)
                                cb = int(220 * disk_int)
                            elif temp > 0.5:
                                # Middle - yellow/orange
                                cr = int(255 * disk_int)
                                cg = int(200 * disk_int)
                                cb = int(80 * disk_int)
                            elif temp > 0.25:
                                # Outer-middle - orange/red
                                cr = int(240 * disk_int)
                                cg = int(130 * disk_int)
                                cb = int(40 * disk_int)
                            else:
                                # Outer edge - deep red
                                cr = int(180 * disk_int)
                                cg = int(60 * disk_int)
                                cb = int(30 * disk_int)

                            # Blue shift on approaching side
                            if doppler > 1.0:
                                cb = min(255, cb + int(80 * (doppler - 1) * disk_int))
                                cg = min(255, cg + int(30 * (doppler - 1) * disk_int))
                            # Red shift on receding side
                            else:
                                cr = min(255, cr + int(50 * (1 - doppler) * disk_int))

                            color = rgb_to_ansi(cr, cg, cb)

                # === RELATIVISTIC JETS ===
                if intensity < 0.5 and r > rs * 1.3 and r < disk_outer * 0.7:
                    angle = math.atan2(ny, nx)
                    # Jets at poles (top and bottom)
                    angle_from_pole = min(abs(angle - 1.5708), abs(angle + 1.5708))

                    if angle_from_pole < 0.2:
                        jet_int = (1.0 - angle_from_pole / 0.2)
                        jet_int *= (1.0 - r / (disk_outer * 0.7))

                        # Helical structure
                        helix = 0.5 + 0.5 * self._fast_sin(r * 40 - t4 + angle * 3)
                        jet_int *= helix

                        # Collimation - tighter near base
                        collimate = 1.0 - 0.5 * (r / (disk_outer * 0.7))
                        jet_int *= collimate

                        if jet_int > intensity and jet_int > 0.12:
                            intensity = jet_int
                            idx = min(7, int(jet_int * 7))
                            char = self.chars[idx]
                            # Blue/cyan jets
                            color = rgb_to_ansi(
                                int(80 * jet_int),
                                int(150 * jet_int),
                                int(230 * jet_int)
                            )

                # === GRAVITATIONALLY LENSED STARFIELD ===
                if color is None and r > rs * 1.5:
                    for sx, sy, bright, phase, tint in self.stars:
                        # Apply inverse lensing to star positions
                        star_r = math.sqrt(sx * sx + sy * sy)
                        if star_r > 0.1:
                            # Stars appear distorted/stretched near black hole
                            lens_factor = 1.0 + deflection * 2
                            lensed_sx = sx * lens_factor
                            lensed_sy = sy * lens_factor

                            dx = nx - lensed_sx
                            dy = ny - lensed_sy

                            if abs(dx) < 0.05 and abs(dy) < 0.05:
                                d_sq = dx * dx + dy * dy

                                # Stars stretch into arcs near Einstein ring
                                stretch = 1.0 + deflection * 3
                                threshold = 0.002 * stretch

                                if d_sq < threshold:
                                    twinkle = 0.7 + 0.3 * self._fast_sin(t2 + phase)
                                    star_b = bright * twinkle

                                    # Brightening due to lensing
                                    star_b *= (1.0 + deflection * 2)

                                    if star_b > 0.25:
                                        intensity = star_b
                                        char = '·' if star_b < 0.5 else '∙' if star_b < 0.75 else '+'

                                        # Star colors
                                        if tint < 0.1:
                                            # Blue star
                                            color = rgb_to_ansi(
                                                int(180 * star_b),
                                                int(200 * star_b),
                                                int(255 * star_b)
                                            )
                                        elif tint < 0.2:
                                            # Red giant
                                            color = rgb_to_ansi(
                                                int(255 * star_b),
                                                int(150 * star_b),
                                                int(100 * star_b)
                                            )
                                        else:
                                            # White/yellow
                                            color = rgb_to_ansi(
                                                int(240 * star_b),
                                                int(235 * star_b),
                                                int(200 * star_b)
                                            )
                                        break

                # === WARPED SPACETIME GRID (subtle) ===
                if color is None and r > disk_outer * 0.8:
                    # Grid lines that curve near black hole
                    grid_spacing = 0.12
                    grid_x = (lensed_x % grid_spacing) / grid_spacing
                    grid_y = (lensed_y % grid_spacing) / grid_spacing

                    # Lines at 0 and 1 of each cell
                    on_line = min(grid_x, 1 - grid_x) < 0.08 or min(grid_y, 1 - grid_y) < 0.08

                    if on_line:
                        grid_int = 0.15 * (1.0 - r)  # Fade with distance
                        if grid_int > 0.05:
                            char = '·'
                            c = int(60 * grid_int / 0.15)
                            color = rgb_to_ansi(c, c, int(c * 1.3))

                row_chars.append(char)
                row_colors.append(color)

            # Build row string
            row = ""
            for i in range(width):
                c = row_colors[i]
                ch = row_chars[i]
                row += (c + ch) if c else ch
            output.append(row + reset_color())

        return output
