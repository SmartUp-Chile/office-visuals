import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class WavesVisual(VisualBase):
    """Ocean-like wave patterns with rainbow colors"""
    
    metadata = {
        "name": "Ocean Waves",
        "author": "sat",
        "version": "1.0",
        "description": "Flowing wave patterns with rainbow colors"
    }
    
    def generate_frame(self, width, height, time_offset):
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                # Multiple wave functions for trippy effect
                wave1 = math.sin((x * 0.1) + (time_offset * 2)) * 0.5
                wave2 = math.cos((y * 0.2) + (time_offset * 1.5)) * 0.5
                wave3 = math.sin(((x + y) * 0.05) + (time_offset * 3)) * 0.3
                
                combined = wave1 + wave2 + wave3
                
                # Convert to RGB colors
                r = int((math.sin(combined + time_offset) + 1) * 127)
                g = int((math.sin(combined + time_offset + 2) + 1) * 127)
                b = int((math.sin(combined + time_offset + 4) + 1) * 127)
                
                # Choose character based on wave intensity
                chars = " ░▒▓█▓▒░"
                char_index = int((combined + 1) * 3.5)
                char_index = max(0, min(len(chars) - 1, char_index))
                
                char = chars[char_index]
                color = rgb_to_ansi(r, g, b)
                row += color + char
            
            pattern.append(row + reset_color())
        return pattern