import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class SpiralVisual(VisualBase):
    """Hypnotic spiral patterns radiating from center"""
    
    metadata = {
        "name": "Hypnotic Spiral", 
        "author": "sat",
        "version": "1.0",
        "description": "Mesmerizing spiral patterns radiating from center"
    }
    
    def generate_frame(self, width, height, time_offset):
        pattern = []
        center_x, center_y = width // 2, height // 2
        
        for y in range(height):
            row = ""
            for x in range(width):
                # Distance from center
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                angle = math.atan2(dy, dx)
                
                # Spiral effect
                spiral_val = math.sin(distance * 0.3 - time_offset * 2) * math.cos(angle * 3 + time_offset)
                
                # Color based on spiral value and position
                r = int((math.sin(spiral_val + time_offset) + 1) * 127)
                g = int((math.cos(spiral_val + time_offset + 1) + 1) * 127)  
                b = int((math.sin(spiral_val + time_offset + 2) + 1) * 127)
                
                # Character selection
                chars = " ·:;+=xX$&"
                char_index = int((spiral_val + 1) * 4.5)
                char_index = max(0, min(len(chars) - 1, char_index))
                
                char = chars[char_index]
                color = rgb_to_ansi(r, g, b)
                row += color + char
                
            pattern.append(row + reset_color())
        return pattern