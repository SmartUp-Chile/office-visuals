import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class ChileanFlagVisual(VisualBase):
    """Chilean flag with animated star effect"""

    metadata = {
        "name": "Chilean Flag",
        "author": "Manu",
        "version": "1.0",
        "description": "Chilean flag with animated star and wave effects"
    }

    def __init__(self):
        # Chilean flag colors (RGB)
        self.blue = rgb_to_ansi(0, 56, 147)     # Blue square
        self.red = rgb_to_ansi(217, 16, 35)     # Red stripe
        self.white = rgb_to_ansi(255, 255, 255) # White stripes

        # Star points for 5-pointed star
        self.star_points = []
        for i in range(5):
            angle = i * 2 * math.pi / 5 - math.pi / 2
            self.star_points.append((math.cos(angle), math.sin(angle)))

        # Inner star points (between the main points)
        self.inner_star_points = []
        for i in range(5):
            angle = (i + 0.5) * 2 * math.pi / 5 - math.pi / 2
            self.inner_star_points.append((math.cos(angle) * 0.4, math.sin(angle) * 0.4))

    def point_in_star(self, x, y, cx, cy, size, rotation=0):
        """Check if point (x,y) is inside a 5-pointed star centered at (cx,cy)"""
        # Translate to star center
        dx, dy = x - cx, y - cy

        # Apply rotation
        if rotation != 0:
            cos_r, sin_r = math.cos(rotation), math.sin(rotation)
            dx, dy = dx * cos_r - dy * sin_r, dx * sin_r + dy * cos_r

        # Scale
        dx, dy = dx / size, dy / size

        # Distance from center
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 1:
            return False

        # Angle from center
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi

        # Check if point is in one of the 5 triangular sections of the star
        section_angle = 2 * math.pi / 5
        section = int(angle / section_angle)
        local_angle = angle - section * section_angle

        # Simple star approximation using distance modulation
        star_radius = 0.5 + 0.5 * math.cos(5 * angle)
        return distance <= star_radius

    def generate_frame(self, width, height, time_offset):
        pattern = []

        # Use full screen dimensions
        flag_width = width
        flag_height = height

        # Flag starts at top-left corner
        start_x = 0
        start_y = 0

        # Blue square is 1/3 of flag width and 1/2 of flag height
        blue_width = flag_width // 3
        blue_height = flag_height // 2

        # Star parameters
        star_size = min(blue_width, blue_height) // 4
        star_x = start_x + blue_width // 2
        star_y = start_y + blue_height // 2
        star_rotation = time_offset * 0.5  # Slow rotation
        star_pulse = 1.0 + 0.3 * math.sin(time_offset * 3)  # Pulsing effect

        for y in range(height):
            row = ""
            for x in range(width):
                char = " "
                color = ""

                # Check if we're inside the flag area
                if (start_x <= x < start_x + flag_width and
                    start_y <= y < start_y + flag_height):

                    fx, fy = x - start_x, y - start_y

                    # Blue square (top-left)
                    if fx < blue_width and fy < blue_height:
                        color = self.blue
                        char = "█"

                        # Add animated star
                        if self.point_in_star(x, y, star_x, star_y,
                                            star_size * star_pulse, star_rotation):
                            color = self.white
                            char = "★"

                    # White stripe (top-right)
                    elif fx >= blue_width and fy < blue_height:
                        color = self.white
                        char = "█"

                        # Add subtle wave effect
                        wave = math.sin((fx - blue_width) * 0.3 + time_offset * 2)
                        if wave > 0.7:
                            char = "▓"

                    # Red stripe (bottom)
                    elif fy >= blue_height:
                        color = self.red
                        char = "█"

                        # Add subtle wave effect
                        wave = math.sin(fx * 0.2 + time_offset * 1.5)
                        if wave > 0.8:
                            char = "▓"


                row += color + char

            pattern.append(row + reset_color())

        return pattern