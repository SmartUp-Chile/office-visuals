import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class IntelligenceVisual(VisualBase):
    """AGI/ASI-inspired abstract: neural constellations, spirals, and pulses"""

    metadata = {
        "name": "Intelligence",
        "author": "sat",
        "version": "1.0",
        "description": "Trippy neural-spiral lattice with living AGI/ASI energy"
    }

    def __init__(self):
        # Constellation node layout (normalized polar anchors)
        random.seed(42)
        self.node_count = 8
        # Angles spaced around a circle, with slight jitter for organic feel
        self.node_angles = [
            (2 * math.pi * i / self.node_count) + random.uniform(-0.12, 0.12)
            for i in range(self.node_count)
        ]
        # Radii in [0.32, 0.48] of min dimension
        self.node_radii = [
            0.32 + 0.16 * random.random()
            for _ in range(self.node_count)
        ]
        
        # Character ramp from light to dense
        self.char_ramp = [
            " ", "·", ".", "•", "○", "◦", "✦", "◆", "█"
        ]

    def _palette(self, h, i):
        """Neon triadic palette. h in radians, i intensity [0,1]."""
        # Base neon via phased sines; modulate by intensity i
        r = 128 + 127 * math.sin(h + 0.0)
        g = 128 + 127 * math.sin(h + 2.094)  # +120°
        b = 128 + 127 * math.sin(h + 4.188)  # +240°
        # Bias toward cyber cyan/magenta at low intensities, gold at peaks
        boost = i ** 1.6
        r = r * (0.6 + 0.4 * boost) + 40 * boost
        g = g * (0.6 + 0.4 * boost) + 20 * (1.0 - boost)
        b = b * (0.7 + 0.3 * boost) + 60 * (1.0 - boost)
        return max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

    def generate_frame(self, width, height, time_offset):
        cx, cy = width / 2.0, height / 2.0
        # Normalize for terminal cell aspect (roughly 2:1 height to width)
        aspect_y = 2.0
        t = time_offset

        # Precompute node positions for this frame
        min_dim = min(width, height * aspect_y)
        nodes = []
        for ang, rad in zip(self.node_angles, self.node_radii):
            r = rad * min_dim
            nx = cx + math.cos(ang + t * 0.12) * r
            ny = cy + math.sin(ang + t * 0.12) * (r / aspect_y)
            nodes.append((nx, ny))

        pattern = []

        for y in range(height):
            row = ""
            for x in range(width):
                # Center-relative coords with aspect correction
                dx = (x - cx)
                dy = (y - cy) * aspect_y
                r = math.hypot(dx, dy) + 1e-6
                a = math.atan2(dy, dx)

                # Multi-field synthesis:
                # 1) Spiral cognitive field
                spiral = math.sin(3.0 * a + 0.35 * r - 1.2 * t)

                # 2) Interference lattice (order within chaos)
                lattice = (
                    math.sin(0.18 * (dx + dy) + 0.7 * t) *
                    math.cos(0.14 * (dx - dy) - 0.9 * t)
                )

                # 3) Radial ring pulses (emergent learning waves)
                rings = math.cos(0.27 * r - 2.0 * t)

                # 4) Neuron node proximity with beating glow
                closest = 1e9
                for nx, ny in nodes:
                    ndx, ndy = x - nx, (y - ny)
                    d = math.hypot(ndx, ndy * aspect_y)
                    if d < closest:
                        closest = d
                node_field = math.exp(-0.09 * (closest ** 2)) * (1.0 + 0.6 * math.sin(t * 3.0 + closest * 0.4))

                # Combine fields
                val = 0.55 * spiral + 0.45 * lattice + 0.35 * rings + 1.1 * node_field
                # Focus bias toward a fractal-like core
                core = math.sin(0.11 * r - 0.8 * t)
                val += 0.25 * core

                # Normalize to [0,1]
                intensity = 0.5 + 0.5 * math.tanh(val)

                # Character selection
                idx = int(intensity * (len(self.char_ramp) - 1))
                idx = max(0, min(len(self.char_ramp) - 1, idx))
                ch = self.char_ramp[idx]

                # Color hue driven by angle, radial drift, and time
                hue = a + 0.15 * r + 0.9 * t + 0.6 * math.sin(0.05 * r - 0.7 * t)
                r8, g8, b8 = self._palette(hue, intensity)
                color = rgb_to_ansi(r8, g8, b8)

                # Slightly reduce color for very low intensities to keep contrast clean
                if intensity < 0.1:
                    color = ""

                row += (color + ch) if color else ch

            pattern.append(row + reset_color())

        return pattern

