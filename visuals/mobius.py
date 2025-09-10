import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class MobiusVisual(VisualBase):
    """3D rotating Möbius strip with dynamic colors"""
    
    metadata = {
        "name": "Möbius Strip 3D",
        "author": "sat",
        "version": "1.0", 
        "description": "3D rotating Möbius strip with mathematical precision and flowing colors"
    }
    
    def __init__(self):
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        
    def generate_frame(self, width, height, time_offset):
        # Update rotation angles
        self.rotation_x = time_offset * 0.8
        self.rotation_y = time_offset * 1.2
        self.rotation_z = time_offset * 0.5
        
        # Create frame buffer
        frame_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        color_buffer = [['' for _ in range(width)] for _ in range(height)]
        z_buffer = [[-float('inf') for _ in range(width)] for _ in range(height)]
        
        # Center coordinates
        cx, cy = width // 2, height // 2
        
        # Generate Möbius strip points - more detail for larger size
        u_steps = 120  # Parameter along the strip
        v_steps = 30  # Parameter across the width
        
        for u_i in range(u_steps):
            for v_i in range(v_steps):
                # Parametric equations for Möbius strip
                u = (u_i / u_steps) * 4 * math.pi - 2 * math.pi  # -2π to 2π
                v = (v_i / v_steps) * 2 - 1  # -1 to 1
                
                # Möbius strip parametric equations
                x = (1 + 0.5 * v * math.cos(u/2)) * math.cos(u)
                y = (1 + 0.5 * v * math.cos(u/2)) * math.sin(u)
                z = 0.5 * v * math.sin(u/2)
                
                # Scale the strip - even larger!
                scale = min(width, height) * 0.45
                x *= scale
                y *= scale
                z *= scale
                
                # 3D rotation matrices
                # Rotation around X axis
                y_rot = y * math.cos(self.rotation_x) - z * math.sin(self.rotation_x)
                z_rot = y * math.sin(self.rotation_x) + z * math.cos(self.rotation_x)
                y, z = y_rot, z_rot
                
                # Rotation around Y axis
                x_rot = x * math.cos(self.rotation_y) + z * math.sin(self.rotation_y)
                z_rot = -x * math.sin(self.rotation_y) + z * math.cos(self.rotation_y)
                x, z = x_rot, z_rot
                
                # Rotation around Z axis
                x_rot = x * math.cos(self.rotation_z) - y * math.sin(self.rotation_z)
                y_rot = x * math.sin(self.rotation_z) + y * math.cos(self.rotation_z)
                x, y = x_rot, y_rot
                
                # Project to 2D (perspective projection)
                distance = 200
                if z > -distance:
                    factor = distance / (distance + z)
                    screen_x = int(cx + x * factor)
                    screen_y = int(cy - y * factor * 0.5)  # Compress Y for terminal aspect ratio
                    
                    # Check bounds
                    if 0 <= screen_x < width and 0 <= screen_y < height:
                        # Z-buffer test
                        if z > z_buffer[screen_y][screen_x]:
                            z_buffer[screen_y][screen_x] = z
                            
                            # Choose character based on surface normal/orientation
                            if u_i % 4 == 0 or v_i % 3 == 0:
                                char = '█'
                            elif abs(v) > 0.7:
                                char = '▓'
                            elif abs(v) > 0.4:
                                char = '▒'
                            else:
                                char = '░'
                            
                            frame_buffer[screen_y][screen_x] = char
                            
                            # Dynamic color based on position and time
                            color_phase = u + time_offset * 2
                            r = int(128 + 127 * math.sin(color_phase))
                            g = int(128 + 127 * math.sin(color_phase + 2))
                            b = int(128 + 127 * math.sin(color_phase + 4))
                            
                            # Adjust brightness based on Z (depth)
                            brightness = (z + scale) / (2 * scale)
                            brightness = max(0.3, min(1.0, brightness))
                            
                            r = int(r * brightness)
                            g = int(g * brightness)
                            b = int(b * brightness)
                            
                            color_buffer[screen_y][screen_x] = rgb_to_ansi(r, g, b)
        
        # Add some sparkles on the strip edges
        for _ in range(width // 8):
            for y in range(height):
                for x in range(width):
                    if frame_buffer[y][x] != ' ':
                        # Check if it's an edge (has empty neighbor)
                        is_edge = False
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < width and 0 <= ny < height:
                                    if frame_buffer[ny][nx] == ' ':
                                        is_edge = True
                                        break
                            if is_edge:
                                break
                        
                        if is_edge and hash((x, y, int(time_offset * 10))) % 100 < 5:
                            color_buffer[y][x] = rgb_to_ansi(255, 255, 255)
                            frame_buffer[y][x] = '✦'
        
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