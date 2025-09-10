import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class PlasmaVisual(VisualBase):
    """Classic plasma effect with flowing colors"""
    
    metadata = {
        "name": "Plasma Field",
        "author": "sat", 
        "version": "1.0",
        "description": "Classic plasma effect with flowing rainbow colors"
    }
    
    def generate_frame(self, width, height, time_offset):
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                # Plasma algorithm
                v1 = math.sin(x * 0.16 + time_offset)
                v2 = math.sin(y * 0.13 + time_offset)
                v3 = math.sin((x + y) * 0.12 + time_offset)
                v4 = math.sin(math.sqrt(x*x + y*y) * 0.1 + time_offset)
                
                plasma = (v1 + v2 + v3 + v4) / 4
                
                # Rainbow colors
                hue = (plasma + 1) * 180
                r = int((math.sin(math.radians(hue)) + 1) * 127)
                g = int((math.sin(math.radians(hue + 120)) + 1) * 127)
                b = int((math.sin(math.radians(hue + 240)) + 1) * 127)
                
                # Block characters for solid effect
                chars = " ▁▂▃▄▅▆▇█"
                char_index = int((plasma + 1) * 4)
                char_index = max(0, min(len(chars) - 1, char_index))
                
                char = chars[char_index]
                color = rgb_to_ansi(r, g, b)
                row += color + char
                
            pattern.append(row + reset_color())
        return pattern