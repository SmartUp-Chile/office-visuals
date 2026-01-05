import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class BreathingGeometryVisual(VisualBase):
    """Massive sacred geometry filling the screen"""

    metadata = {
        "name": "Breathing Geometry",
        "author": "sat",
        "version": "3.0",
        "description": "Sacred geometry - massive, immersive, hypnotic",
        "ai_creator": "Claude Opus 4.5"
    }

    def __init__(self):
        # Sin lookup for speed - 128 entries for smoother curves
        self.sin_lut = [math.sin(i * 6.28318 / 128) for i in range(128)]
        self.cos_lut = [math.cos(i * 6.28318 / 128) for i in range(128)]

        # Characters - bold and defined
        self.chars = " ·∙○●◉◈█"

    def _fast_sin(self, x):
        return self.sin_lut[int((x % 6.28318) * 20.37) & 127]

    def _fast_cos(self, x):
        return self.cos_lut[int((x % 6.28318) * 20.37) & 127]

    def _flower_of_life(self, x, y, t, scale):
        """Full flower of life - 3 rings of circles"""
        intensity = 0

        breath = 1.0 + 0.12 * self._fast_sin(t * 0.4)
        base_radius = 0.12 * scale * breath

        # Thicker lines
        line_width = base_radius * 0.12

        # Build circles: center + 3 rings
        circles = [(0, 0, base_radius)]

        # First ring - 6 circles
        for i in range(6):
            a = i * 1.047 + t * 0.08
            circles.append((
                base_radius * 2 * self._fast_cos(a),
                base_radius * 2 * self._fast_sin(a),
                base_radius
            ))

        # Second ring - 12 circles (between first ring)
        for i in range(12):
            a = i * 0.5236 + t * 0.06
            r = base_radius * 3.46  # sqrt(12) roughly
            circles.append((
                r * self._fast_cos(a),
                r * self._fast_sin(a),
                base_radius
            ))

        # Third ring - 18 circles (outer)
        for i in range(18):
            a = i * 0.349 + t * 0.04
            r = base_radius * 4
            circles.append((
                r * self._fast_cos(a),
                r * self._fast_sin(a),
                base_radius
            ))

        for cx, cy, rad in circles:
            dist_to_center = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            dist_to_edge = abs(dist_to_center - rad)

            if dist_to_edge < line_width:
                edge_int = 1.0 - (dist_to_edge / line_width) ** 0.4
                intensity = max(intensity, edge_int)

        return intensity

    def _hexagram(self, x, y, t, scale):
        """Massive Star of David with inner patterns"""
        intensity = 0

        rot = t * 0.15
        size = scale * 0.55 * (1.0 + 0.08 * self._fast_sin(t * 0.3))
        line_width = scale * 0.02

        # Main hexagram - two triangles
        for tri in range(2):
            tri_rot = rot + tri * 0.523

            for i in range(3):
                a1 = tri_rot + i * 2.094
                a2 = tri_rot + (i + 1) * 2.094

                x1, y1 = size * self._fast_cos(a1), size * self._fast_sin(a1)
                x2, y2 = size * self._fast_cos(a2), size * self._fast_sin(a2)

                dx, dy = x2 - x1, y2 - y1
                length_sq = dx * dx + dy * dy
                if length_sq > 0:
                    t_param = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
                    px, py = x1 + t_param * dx, y1 + t_param * dy
                    dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)

                    if dist < line_width:
                        intensity = max(intensity, 1.0 - dist / line_width)

        # Inner hexagram (smaller, counter-rotating)
        size2 = size * 0.5
        rot2 = -rot * 1.5
        for tri in range(2):
            tri_rot = rot2 + tri * 0.523

            for i in range(3):
                a1 = tri_rot + i * 2.094
                a2 = tri_rot + (i + 1) * 2.094

                x1, y1 = size2 * self._fast_cos(a1), size2 * self._fast_sin(a1)
                x2, y2 = size2 * self._fast_cos(a2), size2 * self._fast_sin(a2)

                dx, dy = x2 - x1, y2 - y1
                length_sq = dx * dx + dy * dy
                if length_sq > 0:
                    t_param = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
                    px, py = x1 + t_param * dx, y1 + t_param * dy
                    dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)

                    if dist < line_width * 0.8:
                        intensity = max(intensity, 0.85 * (1.0 - dist / (line_width * 0.8)))

        # Central hexagon
        hex_r = size * 0.22
        for i in range(6):
            a1 = rot + i * 1.047
            a2 = rot + (i + 1) * 1.047
            x1, y1 = hex_r * self._fast_cos(a1), hex_r * self._fast_sin(a1)
            x2, y2 = hex_r * self._fast_cos(a2), hex_r * self._fast_sin(a2)

            dx, dy = x2 - x1, y2 - y1
            length_sq = dx * dx + dy * dy
            if length_sq > 0:
                t_param = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
                px, py = x1 + t_param * dx, y1 + t_param * dy
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)

                if dist < line_width * 0.7:
                    intensity = max(intensity, 0.9 * (1.0 - dist / (line_width * 0.7)))

        return intensity

    def _metatron(self, x, y, t, scale):
        """Full Metatron's Cube - all 13 circles connected"""
        intensity = 0

        rot = t * 0.1
        line_width = scale * 0.018

        # 13 vertices of Metatron's Cube
        vertices = [(0, 0)]  # Center

        # Inner hexagon (6 points)
        inner_r = scale * 0.2
        for i in range(6):
            a = rot + i * 1.047
            vertices.append((inner_r * self._fast_cos(a), inner_r * self._fast_sin(a)))

        # Outer hexagon (6 points, offset by 30 degrees)
        outer_r = scale * 0.45
        for i in range(6):
            a = rot + i * 1.047 + 0.523
            vertices.append((outer_r * self._fast_cos(a), outer_r * self._fast_sin(a)))

        # Draw circles at each vertex
        circle_r = inner_r * 0.6
        for vx, vy in vertices:
            dist_to_center = math.sqrt((x - vx) ** 2 + (y - vy) ** 2)
            dist_to_edge = abs(dist_to_center - circle_r)
            if dist_to_edge < line_width:
                c_int = 1.0 - (dist_to_edge / line_width) ** 0.5
                intensity = max(intensity, c_int * 0.7)

        # Connect ALL vertices (the key characteristic)
        all_lines = []

        # Connect center to all
        for i in range(1, 13):
            all_lines.append((vertices[0], vertices[i]))

        # Connect inner hexagon
        for i in range(6):
            all_lines.append((vertices[1 + i], vertices[1 + (i + 1) % 6]))

        # Connect outer hexagon
        for i in range(6):
            all_lines.append((vertices[7 + i], vertices[7 + (i + 1) % 6]))

        # Connect inner to outer (full mesh)
        for i in range(6):
            all_lines.append((vertices[1 + i], vertices[7 + i]))
            all_lines.append((vertices[1 + i], vertices[7 + (i + 1) % 6]))
            all_lines.append((vertices[1 + i], vertices[7 + (i + 5) % 6]))

        # Draw all lines
        for (x1, y1), (x2, y2) in all_lines:
            dx, dy = x2 - x1, y2 - y1
            length_sq = dx * dx + dy * dy
            if length_sq > 0.0001:
                t_param = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
                px, py = x1 + t_param * dx, y1 + t_param * dy
                dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)

                if dist < line_width:
                    line_int = 1.0 - (dist / line_width) ** 0.6
                    intensity = max(intensity, line_int * 0.85)

        # Bright vertices
        for vx, vy in vertices:
            dist = math.sqrt((x - vx) ** 2 + (y - vy) ** 2)
            if dist < line_width * 2.5:
                v_int = 1.0 - dist / (line_width * 2.5)
                intensity = max(intensity, v_int)

        return intensity

    def _sri_yantra(self, x, y, t, scale):
        """Sri Yantra - 9 interlocking triangles"""
        intensity = 0

        rot = t * 0.08
        line_width = scale * 0.015

        # Outer circle
        outer_r = scale * 0.5
        dist_to_circle = abs(math.sqrt(x * x + y * y) - outer_r)
        if dist_to_circle < line_width:
            intensity = max(intensity, 0.6 * (1.0 - dist_to_circle / line_width))

        # 9 triangles (4 pointing up, 5 pointing down) at different scales
        triangles = [
            (0.45, 0, True),   # Largest up
            (0.42, 0.1, False),
            (0.38, 0.05, True),
            (0.34, 0.15, False),
            (0.30, 0.1, True),
            (0.26, 0.2, False),
            (0.22, 0.15, True),
            (0.18, 0.25, False),
            (0.12, 0.22, False),
        ]

        for tri_scale, y_offset, pointing_up in triangles:
            size = scale * tri_scale
            base_rot = rot if pointing_up else rot + 3.14159

            for i in range(3):
                a1 = base_rot + i * 2.094 - 1.57
                a2 = base_rot + (i + 1) * 2.094 - 1.57

                x1 = size * self._fast_cos(a1)
                y1 = size * self._fast_sin(a1) + (y_offset * scale if not pointing_up else -y_offset * scale)
                x2 = size * self._fast_cos(a2)
                y2 = size * self._fast_sin(a2) + (y_offset * scale if not pointing_up else -y_offset * scale)

                dx, dy = x2 - x1, y2 - y1
                length_sq = dx * dx + dy * dy
                if length_sq > 0:
                    t_param = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / length_sq))
                    px, py = x1 + t_param * dx, y1 + t_param * dy
                    dist = math.sqrt((x - px) ** 2 + (y - py) ** 2)

                    if dist < line_width:
                        intensity = max(intensity, 1.0 - dist / line_width)

        # Central bindu (dot)
        bindu_dist = math.sqrt(x * x + y * y)
        if bindu_dist < line_width * 3:
            intensity = max(intensity, 1.0 - bindu_dist / (line_width * 3))

        return intensity

    def _torus(self, x, y, t, scale):
        """Torus/donut shape with grid lines"""
        intensity = 0

        r = math.sqrt(x * x + y * y)
        angle = math.atan2(y, x)

        # Torus parameters
        R = scale * 0.35  # Major radius
        tube_r = scale * 0.15  # Tube radius

        line_width = scale * 0.012

        # Multiple rotating torus cross-sections
        for phase in range(8):
            phase_angle = phase * 0.785 + t * 0.3

            # Torus center for this slice
            cx = R * self._fast_cos(phase_angle)
            cy = R * self._fast_sin(phase_angle) * 0.4  # Flatten for perspective

            dist_to_tube = abs(math.sqrt((x - cx) ** 2 + (y - cy) ** 2) - tube_r)
            if dist_to_tube < line_width:
                ring_int = 1.0 - dist_to_tube / line_width
                # Fade based on phase for 3D effect
                depth = 0.5 + 0.5 * self._fast_cos(phase_angle)
                intensity = max(intensity, ring_int * depth * 0.8)

        # Radial grid lines
        num_lines = 12
        for i in range(num_lines):
            line_angle = i * 6.28318 / num_lines + t * 0.2

            # Check if point is near this radial line
            angle_diff = abs(((angle - line_angle + 3.14159) % 6.28318) - 3.14159)
            if angle_diff < 0.05 and R - tube_r < r < R + tube_r:
                line_int = (1.0 - angle_diff / 0.05) * 0.6
                intensity = max(intensity, line_int)

        return intensity

    def generate_frame(self, width, height, time_offset):
        t = time_offset
        cx, cy = width * 0.5, height * 0.5
        aspect = 2.0

        # MUCH BIGGER - use 85% of screen
        scale = min(width, height * aspect) * 0.85

        # Cycle through 5 patterns
        cycle = 15.0
        pattern = int((t / cycle) % 5)

        output = []

        for y_pos in range(height):
            row = ""

            for x_pos in range(width):
                x = (x_pos - cx)
                y = (y_pos - cy) * aspect

                intensity = 0

                if pattern == 0:
                    intensity = self._flower_of_life(x, y, t, scale)
                elif pattern == 1:
                    intensity = self._hexagram(x, y, t, scale)
                elif pattern == 2:
                    intensity = self._metatron(x, y, t, scale)
                elif pattern == 3:
                    intensity = self._sri_yantra(x, y, t, scale)
                else:
                    intensity = self._torus(x, y, t, scale)

                if intensity > 0.08:
                    # Character selection - sharper thresholds
                    if intensity > 0.85:
                        char = '█'
                    elif intensity > 0.7:
                        char = '◈'
                    elif intensity > 0.55:
                        char = '◉'
                    elif intensity > 0.4:
                        char = '●'
                    elif intensity > 0.25:
                        char = '○'
                    elif intensity > 0.15:
                        char = '∙'
                    else:
                        char = '·'

                    # Rich color palette
                    r_dist = math.sqrt(x * x + y * y)
                    angle = math.atan2(y, x)

                    # Different color schemes per pattern
                    if pattern == 0:  # Flower - golden/white
                        hue = angle * 0.5 + t * 0.2
                        cr = int((220 + 35 * self._fast_sin(hue)) * intensity)
                        cg = int((180 + 50 * self._fast_sin(hue + 1)) * intensity)
                        cb = int((100 + 80 * self._fast_sin(hue + 2)) * intensity)
                    elif pattern == 1:  # Hexagram - purple/blue
                        hue = r_dist * 0.015 + t * 0.25
                        cr = int((160 + 80 * self._fast_sin(hue)) * intensity)
                        cg = int((80 + 100 * self._fast_sin(hue + 2)) * intensity)
                        cb = int((220 + 35 * self._fast_sin(hue + 4)) * intensity)
                    elif pattern == 2:  # Metatron - cyan/white
                        hue = angle + r_dist * 0.01 + t * 0.3
                        cr = int((140 + 80 * self._fast_sin(hue)) * intensity)
                        cg = int((200 + 55 * self._fast_sin(hue + 1.5)) * intensity)
                        cb = int((230 + 25 * self._fast_sin(hue + 3)) * intensity)
                    elif pattern == 3:  # Sri Yantra - red/orange/gold
                        hue = r_dist * 0.02 + t * 0.15
                        cr = int((230 + 25 * self._fast_sin(hue)) * intensity)
                        cg = int((120 + 80 * self._fast_sin(hue + 1.5)) * intensity)
                        cb = int((50 + 60 * self._fast_sin(hue + 3)) * intensity)
                    else:  # Torus - rainbow
                        hue = angle + r_dist * 0.02 + t * 0.4
                        cr = int((180 + 75 * self._fast_sin(hue)) * intensity)
                        cg = int((180 + 75 * self._fast_sin(hue + 2.1)) * intensity)
                        cb = int((180 + 75 * self._fast_sin(hue + 4.2)) * intensity)

                    color = rgb_to_ansi(
                        max(0, min(255, cr)),
                        max(0, min(255, cg)),
                        max(0, min(255, cb))
                    )
                    row += color + char
                else:
                    row += ' '

            output.append(row + reset_color())

        return output
