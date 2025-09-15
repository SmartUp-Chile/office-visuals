import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class HyperbolicPurpleVisual(VisualBase):
    """Psychedelic purple hyperbolic geometry in Poincaré disk model"""
    
    metadata = {
        "name": "Hyperbolic Purple Dream",
        "author": "danilo",
        "version": "1.0",
        "description": "Psychedelic purple visualization of hyperbolic geometry with flowing patterns"
    }
    
    def __init__(self):
        self.time = 0
        
    def hyperbolic_distance(self, p1, p2):
        """Calculate hyperbolic distance between two points in Poincaré disk"""
        x1, y1 = p1
        x2, y2 = p2
        
        # Euclidean distance
        d_euclidean = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Points' distances from origin
        r1 = math.sqrt(x1**2 + y1**2)
        r2 = math.sqrt(x2**2 + y2**2)
        
        # Avoid division by zero and ensure we're in unit disk
        if r1 >= 1 or r2 >= 1:
            return float('inf')
            
        # Hyperbolic distance formula in Poincaré disk
        numerator = 2 * d_euclidean**2
        denominator = (1 - r1**2) * (1 - r2**2)
        
        if denominator <= 0:
            return float('inf')
            
        return math.acosh(1 + numerator / denominator)
    
    def hyperbolic_line_point(self, center, radius, angle, t):
        """Get point on hyperbolic line (geodesic circle) at parameter t"""
        # Convert to complex numbers for easier circle math
        center_complex = complex(center[0], center[1])
        
        # Point on the circle
        point = center_complex + radius * complex(math.cos(angle), math.sin(angle))
        
        # Apply hyperbolic transformation
        return point.real, point.imag
    
    def generate_frame(self, width, height, time_offset):
        self.time = time_offset
        
        # Create frame buffer
        frame_buffer = [[' ' for _ in range(width)] for _ in range(height)]
        color_buffer = [['' for _ in range(width)] for _ in range(height)]
        
        # Center and scale for Poincaré disk
        cx, cy = width // 2, height // 2
        radius = min(width, height) * 0.45
        
        # Generate hyperbolic tessellation patterns
        for y in range(height):
            for x in range(width):
                # Convert to disk coordinates [-1, 1]
                disk_x = (x - cx) / radius
                disk_y = (y - cy) / radius
                
                # Only draw inside unit disk
                r = math.sqrt(disk_x**2 + disk_y**2)
                if r >= 1.0:
                    continue
                
                # Multiple layers of hyperbolic patterns
                intensity = 0
                base_color = [80, 20, 120]  # Deep purple base
                
                # Layer 1: Hyperbolic circles (horocycles)
                for i in range(8):
                    angle = (i * math.pi / 4) + time_offset * 0.3
                    center_r = 0.3 + 0.4 * math.sin(time_offset * 0.5 + i)
                    horo_x = center_r * math.cos(angle)
                    horo_y = center_r * math.sin(angle)
                    
                    # Distance to horocycle center
                    dist = math.sqrt((disk_x - horo_x)**2 + (disk_y - horo_y)**2)
                    
                    # Hyperbolic distance effect
                    hyperbolic_factor = 1 / (1 - r**2)
                    wave = math.sin(dist * hyperbolic_factor * 15 + time_offset * 2) * 0.5 + 0.5
                    intensity += wave * (1 - r) * 0.3
                
                # Layer 2: Radial hyperbolic lines
                theta = math.atan2(disk_y, disk_x)
                for i in range(12):
                    line_angle = i * math.pi / 6 + time_offset * 0.4
                    angle_diff = abs(theta - line_angle)
                    angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
                    
                    if angle_diff < 0.2:
                        # Hyperbolic radial distance
                        hyperbolic_r = math.atanh(r) if r < 0.99 else 5
                        wave = math.sin(hyperbolic_r * 3 + time_offset * 3) * 0.5 + 0.5
                        intensity += wave * 0.4
                
                # Layer 3: Spiral patterns in hyperbolic space
                spiral_r = math.atanh(min(r, 0.99))
                spiral_theta = theta * 3 + spiral_r * 2 + time_offset
                spiral_wave = math.sin(spiral_theta) * 0.5 + 0.5
                intensity += spiral_wave * (1 - r**2) * 0.5
                
                # Layer 4: Psychedelic interference patterns
                for freq in [5, 8, 13]:
                    wave1 = math.sin(disk_x * freq + time_offset * 1.5) * 0.5 + 0.5
                    wave2 = math.sin(disk_y * freq * 1.3 + time_offset * 2.1) * 0.5 + 0.5
                    interference = wave1 * wave2
                    intensity += interference * 0.2
                
                # Clamp intensity
                intensity = max(0, min(1, intensity))
                
                # Create psychedelic purple color palette
                if intensity > 0.1:
                    # Multiple purple hues based on position and time
                    hue_shift = math.sin(r * 5 + time_offset) * 0.5 + 0.5
                    brightness = intensity * (0.7 + 0.3 * math.sin(time_offset * 2))
                    
                    # Color variations
                    r_val = int((base_color[0] + hue_shift * 100) * brightness)
                    g_val = int((base_color[1] + hue_shift * 60) * brightness)
                    b_val = int((base_color[2] + 100 + hue_shift * 135) * brightness)
                    
                    # Ensure purple dominance
                    r_val = min(255, max(0, r_val))
                    g_val = min(150, max(0, g_val))  # Keep green low for purple
                    b_val = min(255, max(100, b_val))  # Keep blue high
                    
                    # Character based on intensity
                    if intensity > 0.8:
                        char = '█'
                    elif intensity > 0.6:
                        char = '▓'
                    elif intensity > 0.4:
                        char = '▒'
                    elif intensity > 0.2:
                        char = '░'
                    else:
                        char = '·'
                    
                    # Add some sparkles for psychedelic effect
                    if hash((x, y, int(time_offset * 10))) % 200 < intensity * 10:
                        char = '✦'
                        r_val = min(255, r_val + 50)
                        g_val = min(255, g_val + 30)
                        b_val = min(255, b_val + 50)
                    
                    frame_buffer[y][x] = char
                    color_buffer[y][x] = rgb_to_ansi(r_val, g_val, b_val)
        
        # Add boundary circle with special effects
        for angle_i in range(360):
            angle = math.radians(angle_i)
            # Slightly inside unit circle for visibility
            boundary_r = 0.98
            bound_x = cx + int(boundary_r * radius * math.cos(angle))
            bound_y = cy + int(boundary_r * radius * math.sin(angle))
            
            if 0 <= bound_x < width and 0 <= bound_y < height:
                # Animated boundary
                wave = math.sin(angle_i * 0.1 + time_offset * 3) * 0.5 + 0.5
                brightness = 0.8 + wave * 0.2
                
                frame_buffer[bound_y][bound_x] = '●'
                color_buffer[bound_y][bound_x] = rgb_to_ansi(
                    int(150 * brightness), 
                    int(50 * brightness), 
                    int(200 * brightness)
                )
        
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