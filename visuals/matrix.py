import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class MatrixVisual(VisualBase):
    """Simplified Matrix digital rain"""
    
    metadata = {
        "name": "Digital Matrix Pro",
        "author": "sat",
        "version": "2.1", 
        "description": "Clean Matrix digital rain with green falling code"
    }
    
    def __init__(self):
        self.drops = {}
        self.matrix_chars = [
            "ﾊ", "ﾐ", "ﾋ", "ｰ", "ｳ", "ｼ", "ﾅ", "ﾓ", "ﾆ", "ｻ", "ﾜ", "ﾂ", "ｵ", "ﾘ", "ｱ", "ﾎ", 
            "ﾃ", "ﾏ", "ｹ", "ﾒ", "ｴ", "ｶ", "ｷ", "ﾑ", "ﾕ", "ﾗ", "ｾ", "ﾈ", "ｽ", "ﾀ", "ﾇ", "ﾍ",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            ":", ";", "<", ">", "*", "+", "-", "=", "|", "Z", "I", "O", "N"
        ]
    
    def generate_frame(self, width, height, time_offset):
        # Initialize drops for each column
        if not self.drops:
            for x in range(0, width, 2):  # Every other column
                if random.random() > 0.4:
                    self.drops[x] = {
                        'y': random.randint(-20, -1),
                        'speed': random.uniform(0.5, 2.0),
                        'length': random.randint(8, min(20, height)),
                        'chars': [random.choice(self.matrix_chars) for _ in range(30)]
                    }
        
        # Update drops
        for x, drop in self.drops.items():
            drop['y'] += drop['speed']
            if drop['y'] > height + drop['length']:
                drop['y'] = random.randint(-30, -5)
                drop['speed'] = random.uniform(0.5, 2.0)
                drop['chars'] = [random.choice(self.matrix_chars) for _ in range(30)]
        
        # Generate pattern
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                char = " "
                color = ""
                
                # Check if this position has a matrix character
                if x in self.drops:
                    drop = self.drops[x]
                    drop_y = int(drop['y'])
                    distance = y - drop_y
                    
                    if 0 <= distance < drop['length']:
                        char = drop['chars'][distance % len(drop['chars'])]
                        
                        # Color intensity based on position in drop
                        if distance == 0:
                            # Head - bright white-green
                            color = rgb_to_ansi(200, 255, 200)
                        elif distance < 3:
                            # Near head - bright green
                            color = rgb_to_ansi(0, 255, 100)
                        else:
                            # Tail - fading green
                            intensity = 255 * (1.0 - distance / drop['length'])
                            color = rgb_to_ansi(0, int(intensity), 0)
                
                row += color + char if color else char
            
            pattern.append(row + reset_color())
        
        return pattern