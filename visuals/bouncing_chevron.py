import math
import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class BouncingChevronVisual(VisualBase):
    """Bouncing double chevron with changing purple gradients - DVD logo style"""
    
    metadata = {
        "name": "Bouncing SmartUp",
        "author": "Pablo", 
        "version": "1.0",
        "description": "Purple double chevron bouncing around like the classic DVD logo"
    }
    
    def __init__(self):
        self.x = 10.0
        self.y = 5.0
        self.vel_x = 0.8
        self.vel_y = 0.4
        self.chevron_width = 12
        self.chevron_height = 6
        self.color_cycle = 0.0
        self.trail_particles = []
        
    def get_purple_gradient(self, cycle_time, intensity=1.0):
        """Generate different shades of purple based on cycle time"""
        # Create smooth cycling through different purple gradients
        base_cycle = math.sin(cycle_time * 0.3) * 0.5 + 0.5
        secondary_cycle = math.cos(cycle_time * 0.7) * 0.5 + 0.5
        tertiary_cycle = math.sin(cycle_time * 0.5 + 1.5) * 0.5 + 0.5
        
        # Different purple combinations
        if base_cycle < 0.33:
            # Deep purple to magenta
            r = int((120 + base_cycle * 135) * intensity)
            g = int((50 + base_cycle * 100) * intensity) 
            b = int((200 + base_cycle * 55) * intensity)
        elif base_cycle < 0.66:
            # Purple to violet
            r = int((80 + secondary_cycle * 175) * intensity)
            g = int((30 + secondary_cycle * 120) * intensity)
            b = int((180 + secondary_cycle * 75) * intensity)
        else:
            # Royal purple to bright purple
            r = int((140 + tertiary_cycle * 115) * intensity)
            g = int((20 + tertiary_cycle * 80) * intensity)
            b = int((220 + tertiary_cycle * 35) * intensity)
        
        return min(255, r), min(255, g), min(255, b)
    
    def add_trail_particle(self, x, y, intensity):
        """Add sparkle trail particles"""
        if random.random() < 0.3:  # 30% chance
            self.trail_particles.append({
                'x': x + random.uniform(-1, 1),
                'y': y + random.uniform(-0.5, 0.5),
                'age': 0,
                'max_age': random.randint(15, 30),
                'intensity': intensity * random.uniform(0.5, 1.0),
                'color_offset': random.uniform(0, 2 * math.pi)
            })
    
    def generate_frame(self, width, height, time_offset):
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Bounce off walls (like DVD logo)
        if self.x <= 0 or self.x >= width - self.chevron_width:
            self.vel_x = -self.vel_x
            self.x = max(0, min(width - self.chevron_width, self.x))
            
        if self.y <= 0 or self.y >= height - self.chevron_height:
            self.vel_y = -self.vel_y
            self.y = max(0, min(height - self.chevron_height, self.y))
        
        # Update color cycle
        self.color_cycle += 0.1
        
        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['age'] += 1
            if particle['age'] > particle['max_age']:
                self.trail_particles.remove(particle)
        
        # Create frame buffer
        frame_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        color_buffer = [['' for _ in range(width)] for _ in range(height)]
        
        # Draw trail particles
        for particle in self.trail_particles:
            px, py = int(particle['x']), int(particle['y'])
            if 0 <= px < width and 0 <= py < height:
                fade = max(0.1, 1.0 - particle['age'] / particle['max_age'])
                intensity = particle['intensity'] * fade
                
                if intensity > 0.1:
                    r, g, b = self.get_purple_gradient(
                        self.color_cycle + particle['color_offset'], 
                        intensity * 0.7
                    )
                    char = '✦' if intensity > 0.6 else '·' if intensity > 0.3 else '.'
                    frame_buffer[py][px] = char
                    color_buffer[py][px] = rgb_to_ansi(r, g, b)
        
        # Draw double chevron
        chevron_x = int(self.x)
        chevron_y = int(self.y)
        
        # First chevron (>>)
        chevron_pattern_1 = [
            "  ██    ██",
            " ████  ████",
            "█████████████", 
            " ████  ████",
            "  ██    ██"
        ]
        
        # Second chevron (slightly offset for double effect)  
        chevron_pattern_2 = [
            "    ██    ██  ",
            "   ████  ████ ",
            "  █████████████",
            "   ████  ████ ",
            "    ██    ██  "
        ]
        
        # Draw both chevrons with different purple shades
        for pattern_idx, pattern in enumerate([chevron_pattern_1, chevron_pattern_2]):
            offset_x = pattern_idx * 2
            offset_y = pattern_idx
            
            for row_idx, row in enumerate(pattern):
                for col_idx, char in enumerate(row):
                    draw_x = chevron_x + col_idx + offset_x
                    draw_y = chevron_y + row_idx + offset_y
                    
                    if (0 <= draw_x < width and 0 <= draw_y < height and 
                        char != ' ' and frame_buffer[draw_y][draw_x] == ' '):
                        
                        # Different intensity for each chevron layer
                        intensity = 1.0 if pattern_idx == 0 else 0.8
                        
                        # Get purple color for this position and time
                        color_offset = pattern_idx * 0.5 + (col_idx + row_idx) * 0.1
                        r, g, b = self.get_purple_gradient(
                            self.color_cycle + color_offset, 
                            intensity
                        )
                        
                        # Use different characters for visual depth
                        if char == '█':
                            display_char = '█' if pattern_idx == 0 else '▓'
                        else:
                            display_char = char
                        
                        frame_buffer[draw_y][draw_x] = display_char
                        color_buffer[draw_y][draw_x] = rgb_to_ansi(r, g, b)
                        
                        # Add trail particles from chevron edges
                        if random.random() < 0.05:  # Low chance for performance
                            self.add_trail_particle(draw_x, draw_y, intensity * 0.6)
        
        # Add subtle glow effect around chevron
        glow_radius = 3
        for dy in range(-glow_radius, glow_radius + 1):
            for dx in range(-glow_radius, glow_radius + 1):
                glow_x = chevron_x + self.chevron_width // 2 + dx
                glow_y = chevron_y + self.chevron_height // 2 + dy
                
                if (0 <= glow_x < width and 0 <= glow_y < height and 
                    frame_buffer[glow_y][glow_x] == ' '):
                    
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= glow_radius:
                        glow_intensity = max(0, (glow_radius - distance) / glow_radius) * 0.2
                        
                        if glow_intensity > 0.05:
                            r, g, b = self.get_purple_gradient(self.color_cycle, glow_intensity)
                            frame_buffer[glow_y][glow_x] = '░'
                            color_buffer[glow_y][glow_x] = rgb_to_ansi(r, g, b)
        
        # Add some sparkles around the screen for ambiance
        sparkle_count = 8
        for i in range(sparkle_count):
            sparkle_x = int((math.sin(time_offset * 0.5 + i * 0.8) * 0.4 + 0.5) * width)
            sparkle_y = int((math.cos(time_offset * 0.3 + i * 1.2) * 0.4 + 0.5) * height)
            
            if (0 <= sparkle_x < width and 0 <= sparkle_y < height and 
                frame_buffer[sparkle_y][sparkle_x] == ' '):
                
                sparkle_intensity = (math.sin(time_offset * 2 + i) * 0.3 + 0.7) * 0.4
                if sparkle_intensity > 0.2:
                    r, g, b = self.get_purple_gradient(
                        self.color_cycle + i * 0.7, 
                        sparkle_intensity
                    )
                    frame_buffer[sparkle_y][sparkle_x] = '✦'
                    color_buffer[sparkle_y][sparkle_x] = rgb_to_ansi(r, g, b)
        
        # Convert to pattern format
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                char = frame_buffer[y][x]
                color = color_buffer[y][x]
                row += color + char
            pattern.append(row + reset_color())
        
        return pattern