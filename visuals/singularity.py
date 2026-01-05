import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class SingularityVisual(VisualBase):
    """Falling into the singularity - abstract and immersive"""

    metadata = {
        "name": "Singularity",
        "author": "sat",
        "version": "2.0",
        "description": "The journey into infinite density - abstract spacetime collapse",
        "ai_creator": "Claude Opus 4.5"
    }

    def __init__(self):
        random.seed(42)

        # Pre-compute sin lookup
        self.sin_lut = [math.sin(i * 6.28318 / 128) for i in range(128)]

        # Fewer fragments, bolder
        self.fragments = []
        for _ in range(15):
            self.fragments.append((
                random.random() * 6.28,  # angle
                0.3 + random.random() * 0.6,  # radius
                0.5 + random.random() * 1.5,  # speed
                random.randint(0, 5),  # char type
                random.random() * 6.28,  # hue
            ))

        self.chars = " ·░▒▓█"
        self.frag_chars = "◆◇▲▼●○"

    def _fast_sin(self, x):
        return self.sin_lut[int((x % 6.28318) * 20.37) & 127]

    def generate_frame(self, width, height, time_offset):
        t = time_offset
        cx, cy = width * 0.5, height * 0.5

        # Use more screen space
        scale_x = width * 0.55
        scale_y = height * 1.1

        output = []

        # Pre-calc
        t2 = t * 2
        t3 = t * 3
        t5 = t * 5
        ring_speed = t * 4

        for y in range(height):
            row = ""

            for x in range(width):
                # Normalized coords - fill more space
                nx = (x - cx) / scale_x
                ny = (y - cy) / scale_y

                r = math.sqrt(nx * nx + ny * ny) + 0.001

                char = ' '
                color = None

                # === TUNNEL RINGS (main effect) ===
                # Multiple ring frequencies rushing inward
                ring1 = self._fast_sin((r * 12 - ring_speed) * 3.14)
                ring2 = self._fast_sin((r * 8 - ring_speed * 0.7) * 3.14)
                ring3 = self._fast_sin((r * 20 - ring_speed * 1.5) * 3.14)

                tunnel = (ring1 * 0.5 + ring2 * 0.3 + ring3 * 0.2)
                tunnel = (tunnel + 1) * 0.5  # normalize to 0-1

                # Intensity increases toward center
                center_boost = 1.0 - r * 0.8
                center_boost = max(0.2, min(1, center_boost))

                tunnel *= center_boost

                # Angular variation
                if r > 0.01:
                    angle = math.atan2(ny, nx)
                    angular = 0.7 + 0.3 * self._fast_sin(angle * 6 + t2)
                    tunnel *= angular

                if tunnel > 0.15:
                    idx = min(5, int(tunnel * 5))
                    char = self.chars[idx]

                    # Color: purple/magenta core, red/orange outer
                    hue = r * 3 + t * 0.5
                    cr = int((180 + 75 * self._fast_sin(hue)) * tunnel)
                    cg = int((80 + 60 * self._fast_sin(hue + 2)) * tunnel)
                    cb = int((200 + 55 * self._fast_sin(hue + 4)) * tunnel)

                    # Redshift toward center
                    if r < 0.3:
                        cr = min(255, cr + int(80 * (0.3 - r)))
                        cb = max(0, cb - int(60 * (0.3 - r)))

                    color = rgb_to_ansi(
                        max(0, min(255, cr)),
                        max(0, min(255, cg)),
                        max(0, min(255, cb))
                    )

                # === SINGULARITY CORE ===
                if r < 0.08:
                    core_int = (0.08 - r) / 0.08
                    # Chaotic flicker
                    flicker = 0.5 + 0.5 * self._fast_sin(t * 20 + x * 0.5 + y * 0.7)
                    core_int *= flicker

                    if core_int > 0.3:
                        idx = min(5, int(core_int * 5))
                        char = self.chars[idx]
                        # Blinding white/cyan at singularity
                        c = int(200 + 55 * core_int)
                        color = rgb_to_ansi(c, c, 255)

                # === FRAGMENTS ===
                if color is None or tunnel < 0.3:
                    for f_angle, f_r, f_speed, f_char, f_hue in self.fragments:
                        # Fragment spirals inward
                        curr_r = (f_r - t * f_speed * 0.08) % 0.9
                        curr_angle = f_angle + t * 0.5 + (0.9 - curr_r) * 2

                        fx = curr_r * math.cos(curr_angle)
                        fy = curr_r * math.sin(curr_angle)

                        dx = nx - fx
                        dy = ny - fy

                        if abs(dx) < 0.06 and abs(dy) < 0.06:
                            d = dx * dx + dy * dy
                            if d < 0.003:
                                char = self.frag_chars[f_char]
                                f_int = 0.6 + 0.4 * (1 - curr_r)
                                cr = int((180 + 70 * self._fast_sin(f_hue)) * f_int)
                                cg = int((120 + 80 * self._fast_sin(f_hue + 2)) * f_int)
                                cb = int((200 + 55 * self._fast_sin(f_hue + 4)) * f_int)
                                color = rgb_to_ansi(cr, cg, cb)
                                break

                # === EVENT HORIZON RING ===
                horizon = 0.5 - t * 0.02 % 0.3
                if horizon > 0.15 and abs(r - horizon) < 0.025:
                    ring_int = 1.0 - abs(r - horizon) / 0.025
                    ring_int *= 0.6 + 0.4 * self._fast_sin(math.atan2(ny, nx) * 8 + t3)
                    if ring_int > 0.4:
                        char = '○' if ring_int < 0.7 else '●'
                        color = rgb_to_ansi(
                            int(255 * ring_int),
                            int(140 * ring_int),
                            int(40 * ring_int)
                        )

                row += (color + char) if color else char

            output.append(row + reset_color())

        return output
