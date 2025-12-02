import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class QuantumGhostVisual(VisualBase):
    """
    Clifford Attractor Density Visualization V6 - SINGULARITY
    Features:
    - Persistence Trails
    - Dual Attractors
    - Digital Glitch Artifacts
    - Particle Explosions
    - Binary Rain Overlay
    """
    
    metadata = {
        "name": "Quantum Ghost",
        "author": "Sat (Architeched by Gemini)",
        "version": "6.0", 
        "description": "SINGULARITY: Maximum Density & Chaos"
    }
    
    def __init__(self):
        # Chaos Engines
        self.params_1 = [1.5, -1.8, 1.6, 0.9]
        self.target_1 = self._generate_wild_params()
        self.params_2 = [-1.7, 1.3, -0.1, -1.2]
        self.target_2 = self._generate_wild_params()
        
        # State
        self.palette = self._generate_psychedelic_palette()
        self.chars = "  .:-=+*#%@"
        self.buffer = {} 
        self.width = 0
        self.height = 0
        
        # Effects
        self.particles = [] # Explosions
        self.matrix_drops = {} # Matrix rain
        self.glitch_mode = False

    def _generate_wild_params(self):
        return [random.uniform(-3.0, 3.0) for _ in range(4)]

    def _generate_psychedelic_palette(self):
        palette = []
        for i in range(512): 
            t = i / 511.0
            r = int(127.5 + 127.5 * math.sin(6.28 * t))
            g = int(127.5 + 127.5 * math.sin(6.28 * t + 1.5)) 
            b = int(127.5 + 127.5 * math.sin(6.28 * t + 3.0))
            palette.append(rgb_to_ansi(r, g, b))
        return palette

    def generate_frame(self, width, height, time_offset):
        if width != self.width or height != self.height:
            self.buffer = {}
            self.width = width
            self.height = height

        # 1. Update Chaos Engines
        # -----------------------
        for i in range(4):
            self.params_1[i] += (self.target_1[i] - self.params_1[i]) * 0.02
            self.params_2[i] += (self.target_2[i] - self.params_2[i]) * 0.03
            
            if random.random() > 0.98: self.target_1 = self._generate_wild_params()
            if random.random() > 0.98: self.target_2 = self._generate_wild_params()

        # 2. Core Simulation (Dual Layer)
        # -------------------------------
        density_map = {} # Sparse map
        scale = min(width, height) * 0.45
        cx, cy = width // 2, height // 2
        
        # Function to run solver
        def run_solver(params, count, turbulence_func):
            a, b, c, d = params
            x, y = 0.1, 0.1
            for _ in range(count):
                xn = math.sin(a * y) + c * math.cos(a * x)
                yn = math.sin(b * x) + d * math.cos(b * y)
                x, y = xn, yn
                
                tx, ty = turbulence_func(x, y)
                px = int(cx + tx * scale)
                py = int(cy + ty * scale * 0.5)
                
                if 0 <= px < width and 0 <= py < height:
                    density_map[(px, py)] = density_map.get((px, py), 0) + 1

        # Layer 1: Fluid
        run_solver(self.params_1, 20000, 
                   lambda x, y: (x + 0.2*math.sin(y+time_offset), y + 0.2*math.cos(x+time_offset)))
        
        # Layer 2: Jitter
        run_solver(self.params_2, 20000, 
                   lambda x, y: (x + 0.4*math.cos(y*3), y + 0.4*math.sin(x*3)))

        # 3. Particle System (Explosions)
        # -------------------------------
        # Spawn new particles at high density points
        if density_map:
            # Find a few intense points
            peaks = [k for k, v in density_map.items() if v > 5]
            if peaks and random.random() > 0.5:
                spawn = random.choice(peaks)
                # Boom
                for _ in range(5):
                    self.particles.append({
                        'x': spawn[0], 'y': spawn[1],
                        'vx': random.uniform(-1, 1), 'vy': random.uniform(-0.5, 0.5),
                        'life': 1.0,
                        'color_idx': random.randint(0, 511)
                    })
        
        # Update Particles
        active_particles = []
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 0.05
            if p['life'] > 0:
                active_particles.append(p)
                px, py = int(p['x']), int(p['y'])
                if 0 <= px < width and 0 <= py < height:
                    # Add to density map directly for rendering
                    density_map[(px, py)] = density_map.get((px, py), 0) + 10
        self.particles = active_particles

        # 4. Matrix Rain Overlay (Subtle)
        # -------------------------------
        # Spawn drops
        if random.random() > 0.7:
            col = random.randint(0, width - 1)
            self.matrix_drops[col] = 0
            
        # Update drops
        active_drops = {}
        for col, y_pos in self.matrix_drops.items():
            y_pos += 1
            if y_pos < height:
                active_drops[col] = y_pos
                # Add to density
                density_map[(col, int(y_pos))] = density_map.get((col, int(y_pos)), 0) + 5
        self.matrix_drops = active_drops

        # 5. Buffer & Render
        # ------------------
        # Decay buffer
        remove_keys = []
        for k in self.buffer:
            self.buffer[k] *= 0.85 # Slower decay = longer trails
            if self.buffer[k] < 0.5: remove_keys.append(k)
        for k in remove_keys: del self.buffer[k]
        
        # Add density to buffer
        for k, v in density_map.items():
            self.buffer[k] = self.buffer.get(k, 0) + v * 5

        max_val = 1
        if self.buffer: max_val = max(self.buffer.values())

        # Palette cycling
        shift = int(time_offset * 150) % 512
        
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                # Quad Symmetry
                rx, ry = x, y
                if x > width//2: rx = width-1-x
                if y > height//2: ry = height-1-y
                
                val = self.buffer.get((rx, ry), 0)
                
                # Random Glitch
                if random.random() > 0.999:
                    row += rgb_to_ansi(255, 255, 255) + random.choice(["?", "!", "&", "$"])
                    continue

                if val > 1:
                    norm = math.log(val) / math.log(max_val + 5)
                    norm = min(1.0, norm * 1.4)
                    
                    char_idx = int(norm * (len(self.chars) - 1))
                    char = self.chars[char_idx]
                    
                    # Color
                    col_idx = (int(norm * 400) + shift) % 512
                    color = self.palette[col_idx]
                    
                    row += color + char
                else:
                    # Starfield background (static)
                    if (x * y * 123 + x) % 97 == 0:
                         row += rgb_to_ansi(30, 30, 60) + "."
                    else:
                        row += " "
            pattern.append(row + reset_color())
            
        return pattern
