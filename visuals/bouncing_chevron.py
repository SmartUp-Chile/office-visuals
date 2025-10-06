import math
import sys
import os
import random
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class BouncingChevronVisual(VisualBase):
    """Bouncing double chevron with changing purple gradients - DVD logo style"""
    
    metadata = {
        "name": "Bouncing SmartUp",
        "author": "Pablo", 
        "version": "1.1",
        "description": "Upward double chevron (SmartUp) with bold neon trail and glow"
    }
    
    def __init__(self):
        self.x = 10.0
        self.y = 5.0
        self.vel_x = 0.9
        self.vel_y = 0.5
        # Upward double-chevron made of two stacked outline triangles
        # Each triangle height H -> width W = 2H-1
        self.tri_height = 8
        # Wider via slope scaling (keeps 1-pixel apex, widens sides)
        self.slope_scale = 1.6  # >1 widens horizontally
        self.tri_width = 2 * int((self.tri_height - 1) * self.slope_scale) + 1
        # Overlap amount so the lower chevron tip intrudes into the upper
        self.overlap = max(2, self.tri_height // 3)
        self.chevron_width = self.tri_width
        self.chevron_height = self.tri_height * 2 - self.overlap
        # Debug controls via env vars
        self.debug_static = os.getenv('VISUAL_DEBUG_STATIC', '0') == '1'
        try:
            self.debug_frames = int(os.getenv('VISUAL_DEBUG_FRAMES', '0'))
        except ValueError:
            self.debug_frames = 0
        self.debug_exit = os.getenv('VISUAL_DEBUG_EXIT', '0') == '1'
        self._frame_counter = 0
        self._last_pattern = None
        # Trail growth controls
        self.trail_growth_period = 12
        self.trail_max_thickness = 6  # max edge thickness for ghosts
        self.color_cycle = 0.0
        self.trail_particles = []
        # Ribbon trail of past positions (center points)
        self.history = deque(maxlen=30)
        self.last_bounce = 0
        
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
        # Higher chance to strengthen trails
        if random.random() < 0.6:  # 60% chance
            self.trail_particles.append({
                'x': x + random.uniform(-1, 1),
                'y': y + random.uniform(-0.5, 0.5),
                'age': 0,
                'max_age': random.randint(18, 38),
                'intensity': min(1.0, intensity * random.uniform(0.6, 1.1)),
                'color_offset': random.uniform(0, 2 * math.pi)
            })

    def _draw_triangle_up(self, frame_buffer, color_buffer, top_left_x, top_left_y, main_intensity, color_cycle, ghost_level=0, overwrite=False, edge_thickness=1):
        """Draw a single upward outline triangle (no base line).
        - Only draw slanted edges, omit bottom row to avoid base.
        - ghost_level: 0 main, 1 mid, 2 faint (affects char choice)
        - overwrite: if True, draw even if a cell is occupied (to keep logo above trail)
        - edge_thickness: thickness of each slanted edge in columns
        """
        h = self.tri_height
        w = self.tri_width
        for r in range(h):
            blocks = 1 + 2 * int(r * self.slope_scale)
            pad = (w - blocks) // 2
            # Skip bottom row edges to avoid horizontal base line
            if r == h - 1:
                continue
            # Edge columns in this row
            left_col = pad
            right_col = pad + blocks - 1
            # Thinner tip: single column at the apex
            local_thickness = 1 if r == 0 else edge_thickness
            for tcol in range(local_thickness):
                for c in (left_col + tcol, right_col - tcol):
                    # Keep within this row's triangle span
                    if c < pad or c > pad + blocks - 1:
                        continue
                    draw_x = top_left_x + c
                    draw_y = top_left_y + r
                    if draw_y < 0 or draw_x < 0:
                        continue
                    if draw_y >= len(frame_buffer) or draw_x >= len(frame_buffer[0]):
                        continue
                    if not overwrite and frame_buffer[draw_y][draw_x] != ' ':
                        continue
                    # Character based on ghost level
                    ch = '█' if ghost_level == 0 else ('▓' if ghost_level == 1 else '▒')
                    # Color
                    r8, g8, b8 = self.get_purple_gradient(color_cycle + (r * 0.08 + c * 0.06), main_intensity)
                    frame_buffer[draw_y][draw_x] = ch
                    color_buffer[draw_y][draw_x] = rgb_to_ansi(r8, g8, b8)
                    # Edge sparkles
                    if random.random() < (0.12 if ghost_level == 0 else 0.05):
                        self.add_trail_particle(draw_x, draw_y, main_intensity * (0.9 if ghost_level == 0 else 0.5))

    def generate_frame(self, width, height, time_offset):
        # Debug frame counting / freezing
        self._frame_counter += 1
        freeze = self.debug_static or (self.debug_frames and self._frame_counter > self.debug_frames)
        # Derive a frame index estimate from time_offset for deterministic debug
        frame_index_est = int(time_offset / 0.08 + 0.5)
        # Update position (unless frozen)
        if not freeze:
            self.x += self.vel_x
            self.y += self.vel_y
        
        # Bounce off walls (like DVD logo)
        if not freeze:
            bounced = False
            if self.x <= 0 or self.x >= width - self.chevron_width:
                self.vel_x = -self.vel_x
                self.x = max(0, min(width - self.chevron_width, self.x))
                bounced = True
            if self.y <= 0 or self.y >= height - self.chevron_height:
                self.vel_y = -self.vel_y
                self.y = max(0, min(height - self.chevron_height, self.y))
                bounced = True
            if bounced:
                # Bounce burst of particles
                cx = int(self.x + self.chevron_width // 2)
                cy = int(self.y + self.chevron_height // 2)
                for _ in range(18):
                    self.add_trail_particle(cx, cy, 1.0)
        
        # Update color cycle
        self.color_cycle += 0.1
        
        # Update trail particles (unless frozen)
        if not freeze:
            for particle in self.trail_particles[:]:
                particle['age'] += 1
                if particle['age'] > particle['max_age']:
                    self.trail_particles.remove(particle)
            # Cap particles to avoid buildup
            if len(self.trail_particles) > 1200:
                del self.trail_particles[:len(self.trail_particles) - 1200]

        # Create frame buffer
        frame_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        color_buffer = [['' for _ in range(width)] for _ in range(height)]

        # Update ribbon trail history (use chevron center)
        center_x = self.x + self.chevron_width / 2
        center_y = self.y + self.chevron_height / 2
        self.history.append((center_x, center_y))

        # Draw trail particles
        for particle in self.trail_particles:
            px, py = int(particle['x']), int(particle['y'])
            if 0 <= px < width and 0 <= py < height:
                fade = max(0.1, 1.0 - particle['age'] / particle['max_age'])
                intensity = particle['intensity'] * fade
                
                if intensity > 0.1:
                    r, g, b = self.get_purple_gradient(
                        self.color_cycle + particle['color_offset'], 
                        intensity * 0.9
                    )
                    char = '✦' if intensity > 0.6 else '·' if intensity > 0.3 else '.'
                    frame_buffer[py][px] = char
                    color_buffer[py][px] = rgb_to_ansi(r, g, b)
        # Draw ribbon ghost chevrons from history (thicker, visible trail)
        # Draw older positions first (fainter), skip every 2 for spacing
        if len(self.history) > 3:
            hist = list(self.history)[:-1]
            steps = 8
            # Sample up to 'steps' positions spaced through history
            for i, (hx, hy) in enumerate(hist[::max(1, len(hist)//steps)]):
                # Fainter for older
                age_factor = (i + 1) / (min(steps, len(hist)))
                intensity = 0.22 + 0.38 * (1.0 - age_factor)
                top_left_x = int(hx - self.chevron_width / 2)
                top_left_y = int(hy - self.chevron_height / 2)
                # Trail edge thickness grows every N frames, capped (based on frame index)
                ghost_thickness = 1 + min(self.trail_max_thickness - 1, frame_index_est // self.trail_growth_period)
                # Upper triangle
                self._draw_triangle_up(frame_buffer, color_buffer, top_left_x, top_left_y, intensity, self.color_cycle - age_factor * 0.6, ghost_level=2, edge_thickness=ghost_thickness, overwrite=True)
                # Lower triangle (stacked)
                second_y_hist = top_left_y + self.tri_height - self.overlap
                self._draw_triangle_up(frame_buffer, color_buffer, top_left_x, second_y_hist, intensity * 0.95, self.color_cycle - age_factor * 0.6, ghost_level=2, edge_thickness=ghost_thickness, overwrite=True)

        # Draw main double up-chevron (draw last, overwrite trail/ghost)
        chevron_x = int(self.x)
        chevron_y = int(self.y)
        self._draw_triangle_up(
            frame_buffer, color_buffer, chevron_x, chevron_y,
            1.0, self.color_cycle, ghost_level=0, overwrite=True, edge_thickness=2
        )
        # Second chevron slightly intruding upwards into the first
        second_y = chevron_y + self.tri_height - self.overlap
        self._draw_triangle_up(
            frame_buffer, color_buffer, chevron_x, second_y,
            0.95, self.color_cycle + 0.3, ghost_level=0, overwrite=True, edge_thickness=2
        )

        # If debug requires exiting after N frames, do it after drawing
        if self.debug_exit and self.debug_frames and self._frame_counter >= self.debug_frames:
            raise SystemExit(0)

        # Add subtle glow effect around chevron
        glow_radius = 4
        for dy in range(-glow_radius, glow_radius + 1):
            for dx in range(-glow_radius, glow_radius + 1):
                glow_x = chevron_x + self.chevron_width // 2 + dx
                glow_y = chevron_y + self.chevron_height // 2 + dy
                
                if (0 <= glow_x < width and 0 <= glow_y < height and 
                    frame_buffer[glow_y][glow_x] == ' '):
                    
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= glow_radius:
                        glow_intensity = max(0, (glow_radius - distance) / glow_radius) * 0.3
                        
                        if glow_intensity > 0.05:
                            r, g, b = self.get_purple_gradient(self.color_cycle, glow_intensity)
                            frame_buffer[glow_y][glow_x] = '░'
                            color_buffer[glow_y][glow_x] = rgb_to_ansi(r, g, b)
        
        # Add some sparkles around the screen for ambiance
        sparkle_count = 12
        for i in range(sparkle_count):
            sparkle_x = int((math.sin(time_offset * 0.5 + i * 0.8) * 0.4 + 0.5) * width)
            sparkle_y = int((math.cos(time_offset * 0.3 + i * 1.2) * 0.4 + 0.5) * height)
            
            if (0 <= sparkle_x < width and 0 <= sparkle_y < height and 
                frame_buffer[sparkle_y][sparkle_x] == ' '):
                
                sparkle_intensity = (math.sin(time_offset * 2 + i) * 0.3 + 0.7) * 0.55
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
