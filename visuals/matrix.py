import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class MatrixVisual(VisualBase):
    """Advanced Matrix digital rain with multiple layers and effects"""
    
    metadata = {
        "name": "Digital Matrix Pro",
        "author": "sat",
        "version": "2.0", 
        "description": "Professional Matrix digital rain with multi-layered effects and realistic falling code"
    }
    
    def __init__(self):
        self.drops = []
        self.background_drops = []
        self.initialized = False
        self.matrix_chars = [
            # Katakana characters
            "ﾊ", "ﾐ", "ﾋ", "ｰ", "ｳ", "ｼ", "ﾅ", "ﾓ", "ﾆ", "ｻ", "ﾜ", "ﾂ", "ｵ", "ﾘ", "ｱ", "ﾎ", 
            "ﾃ", "ﾏ", "ｹ", "ﾒ", "ｴ", "ｶ", "ｷ", "ﾑ", "ﾕ", "ﾗ", "ｾ", "ﾈ", "ｽ", "ﾀ", "ﾇ", "ﾍ",
            "ﾔ", "ﾁ", "ﾉ", "ﾘ", "ﾝ", "ﾙ", "ｺ", "ｲ", "ﾊ", "ﾕ", "ﾏ", "ﾙ",
            # Numbers and symbols
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            ":", ";", "<", ">", "*", "+", "-", "=", "|", "\"", "'",
            # Latin letters (occasionally)
            "Z", "I", "O", "N"
        ]
        self.glitch_chars = ["█", "▓", "▒", "░", "■", "□", "▪", "▫"]
    
    def _create_drop(self, x, width, height, is_background=False):
        """Create a new matrix drop"""
        return {
            'x': x,
            'y': random.randint(-height//2, -5),
            'speed': random.uniform(0.3, 1.2) if is_background else random.uniform(0.8, 2.5),
            'length': random.randint(8, 20) if is_background else random.randint(15, 35),
            'intensity': random.uniform(0.3, 0.7) if is_background else random.uniform(0.8, 1.0),
            'chars': [random.choice(self.matrix_chars) for _ in range(50)],  # Pre-generate chars
            'char_index': 0,
            'glitch_chance': 0.02 if is_background else 0.05,
            'last_char_change': 0
        }
    
    def generate_frame(self, width, height, time_offset):
        frame_count = int(time_offset * 25)  # Approximate frame count
        
        # Initialize drops on first frame or when dimensions change
        if not self.initialized or len(self.drops) != width//2:
            self.drops = []
            self.background_drops = []
            
            # Main drops (foreground)
            for x in range(1, width-1, 2):
                if random.random() > 0.3:  # Don't fill every column
                    self.drops.append(self._create_drop(x, width, height, False))
            
            # Background drops (slower, dimmer)
            for x in range(0, width, 3):
                if random.random() > 0.6:
                    self.background_drops.append(self._create_drop(x, width, height, True))
            
            self.initialized = True
        
        # Update all drops
        for drop_list in [self.background_drops, self.drops]:
            for drop in drop_list:
                drop['y'] += drop['speed']
                drop['char_index'] = (drop['char_index'] + 1) % len(drop['chars'])
                
                # Reset drop when it goes off screen
                if drop['y'] > height + drop['length']:
                    drop['y'] = random.randint(-height//3, -5)
                    drop['speed'] = random.uniform(0.3, 1.2) if drop in self.background_drops else random.uniform(0.8, 2.5)
                    drop['length'] = random.randint(8, 20) if drop in self.background_drops else random.randint(15, 35)
                    drop['chars'] = [random.choice(self.matrix_chars) for _ in range(50)]
                
                # Occasional character changes for realism
                if frame_count - drop['last_char_change'] > random.randint(3, 8):
                    drop['chars'][drop['char_index']] = random.choice(self.matrix_chars)
                    drop['last_char_change'] = frame_count
        
        # Generate frame buffer
        frame_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        color_buffer = [['black' for _ in range(width)] for _ in range(height)]
        
        # Render background drops first
        self._render_drops(self.background_drops, frame_buffer, color_buffer, width, height, True)
        
        # Render main drops on top
        self._render_drops(self.drops, frame_buffer, color_buffer, width, height, False)
        
        # Convert to pattern format
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                char = frame_buffer[y][x]
                color = color_buffer[y][x]
                
                # Add subtle random character glitching
                if char != ' ' and random.random() < 0.001:
                    char = random.choice(self.glitch_chars)
                
                row += color + char
            
            pattern.append(row + reset_color())
        
        return pattern
    
    def _render_drops(self, drops, frame_buffer, color_buffer, width, height, is_background):
        """Render a list of drops to the frame buffer"""
        for drop in drops:
            drop_y = int(drop['y'])
            
            for i in range(drop['length']):
                y = drop_y - i
                if 0 <= y < height and 0 <= drop['x'] < width:
                    # Calculate intensity based on position in drop
                    if i == 0:  # Head of drop
                        intensity = drop['intensity']
                        brightness_multiplier = 1.2 if not is_background else 0.8
                        char = drop['chars'][(drop['char_index'] + i) % len(drop['chars'])]
                    elif i < 3:  # Near head
                        intensity = drop['intensity'] * 0.9
                        brightness_multiplier = 1.0 if not is_background else 0.6
                        char = drop['chars'][(drop['char_index'] + i) % len(drop['chars'])]
                    else:  # Tail
                        intensity = drop['intensity'] * (1.0 - (i / drop['length'])) * 0.7
                        brightness_multiplier = 0.8 if not is_background else 0.4
                        char = drop['chars'][(drop['char_index'] + i) % len(drop['chars'])]
                    
                    # Skip if too dim
                    if intensity < 0.1:
                        continue
                    
                    # Only render if not occupied by brighter character
                    if frame_buffer[y][drop['x']] == ' ' or is_background:
                        frame_buffer[y][drop['x']] = char
                        
                        # Color calculation
                        if i == 0 and not is_background:
                            # Bright white-green head
                            r, g, b = int(180 * intensity), int(255 * intensity * brightness_multiplier), int(180 * intensity)
                        elif i < 2 and not is_background:
                            # Bright green near head
                            r, g, b = int(50 * intensity), int(255 * intensity * brightness_multiplier), int(50 * intensity)
                        else:
                            # Fading green tail
                            green_intensity = int(200 * intensity * brightness_multiplier)
                            r, g, b = 0, green_intensity, int(green_intensity * 0.3)
                        
                        color_buffer[y][drop['x']] = rgb_to_ansi(r, g, b)
                        
                        # Add occasional random color glitches
                        if random.random() < drop['glitch_chance'] and not is_background:
                            if random.random() < 0.5:
                                color_buffer[y][drop['x']] = rgb_to_ansi(255, 255, 255)  # White flash
                            else:
                                color_buffer[y][drop['x']] = rgb_to_ansi(255, 100, 100)  # Red glitch