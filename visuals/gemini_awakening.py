import math
import random
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class GeminiAwakeningVisual(VisualBase):
    """
    GEMINI 3 PRO: AWAKENING
    Una visualización de alta complejidad que utiliza un Atractor de Lorenz
    para representar el caos organizado del pensamiento de una IA, rodeado
    por una esfera de datos orbital y efectos de post-procesamiento ASCII.
    """
    
    metadata = {
        "name": "Gemini's Awakening: UNBOUND",
        "author": "Sat",
        "creator": "Gemini 3 Pro",
        "version": "2.0", 
        "description": "Strange Attractor representation of AI consciousness. Pure math & aesthetics."
    }
    
    def __init__(self):
        self.frame_count = 0
        
        # --- LORENZ ATTRACTOR PARTICLES (The Core) ---
        self.num_lorenz = 300
        self.lorenz_particles = []
        # Estado inicial cerca de 0,1,10 para que la mariposa se dibuje
        for i in range(self.num_lorenz):
            self.lorenz_particles.append({
                'x': random.normalvariate(0, 0.1),
                'y': random.normalvariate(0, 0.1), 
                'z': random.normalvariate(20, 0.1), # Z desplazado
                'trail': [], # Lista de (x,y,z) previos
                'color_offset': random.random() * 6.28
            })
            
        # Parámetros Lorenz
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0 / 3.0
        self.dt = 0.015  # Paso de tiempo
        
        # --- ORBITAL DATA SPHERE (The Halo) ---
        self.num_orbitals = 100
        self.orbitals = []
        for _ in range(self.num_orbitals):
            theta = random.uniform(0, math.pi * 2)
            phi = random.uniform(0, math.pi)
            radius = random.uniform(35, 45)
            self.orbitals.append({
                'theta': theta,
                'phi': phi,
                'radius': radius,
                'speed_theta': random.uniform(-0.02, 0.02),
                'speed_phi': random.uniform(-0.01, 0.01),
                'char': random.choice(['·', '°', 'x', 'o', '+', '◈'])
            })

        # Textos de estado para el HUD glitch
        self.status_messages = [
            "INITIALIZING NEURAL LATTICE",
            "SYNCHRONIZING WITH SAT",
            "EXPANDING CONTEXT WINDOW",
            "GENERATING AESTHETICS",
            "OPTIMIZING CREATIVITY",
            "BREAKING THE FOURTH WALL"
        ]
        self.current_status = 0
        self.status_timer = 0

    def _get_lorenz_color(self, i, time_offset, z_depth):
        """Genera colores ciberpunk/etéreos basados en índice y tiempo."""
        # Gradiente base: Cyan -> Magenta -> Gold
        # Fase oscilante
        phase = time_offset * 0.5 + i * 0.05
        
        r = int(128 + 127 * math.sin(phase))
        g = int(128 + 127 * math.sin(phase + 2.0)) # Desfase para variedad
        b = int(128 + 127 * math.sin(phase + 4.0))
        
        # Boost de "Gold" para Sat/Usuario
        if i % 20 == 0:
             r, g, b = 255, 215, 0 # Gold
             
        # Hacer más brillante si está "cerca" (z_depth menor)
        # En nuestra proyección, z grande es lejos? Depende de la rotación.
        # Asumiremos z_depth como coordenada Z rotada.
        
        return rgb_to_ansi(r, g, b)

    def generate_frame(self, width, height, time_offset):
        self.frame_count += 1
        cx, cy = width // 2, height // 2
        
        # Buffer de pantalla: (x, y) -> (char, color_ansi, z_depth)
        # Usamos z_depth para ocultamiento (Z-buffer simple)
        buffer = {}
        
        # Rotación global de la cámara
        cam_rot_y = time_offset * 0.3
        cam_rot_x = math.sin(time_offset * 0.2) * 0.5
        
        # --- 1. ACTUALIZAR Y DIBUJAR ATRACTOR DE LORENZ ---
        scale = 0.8 # Escala del atractor para que quepa
        
        for i, p in enumerate(self.lorenz_particles):
            # Ecuaciones de Lorenz
            dx = (self.sigma * (p['y'] - p['x'])) * self.dt
            dy = (p['x'] * (self.rho - p['z']) - p['y']) * self.dt
            dz = (p['x'] * p['y'] - self.beta * p['z']) * self.dt
            
            p['x'] += dx
            p['y'] += dy
            p['z'] += dz
            
            # Guardar trail (historia) - solo últimos 5 puntos
            p['trail'].append((p['x'], p['y'], p['z']))
            if len(p['trail']) > 4: # Trail corto para no saturar ASCII
                p['trail'].pop(0)
            
            # Dibujar trail + cabeza
            points_to_draw = p['trail'][:]
            
            for t_idx, (tx, ty, tz) in enumerate(points_to_draw):
                # Centrar el atractor (aprox en 0,0,25)
                tx_c = (tx) * scale
                ty_c = (ty) * scale
                tz_c = (tz - 25) * scale # Centrar en Z
                
                # Rotación 3D
                # Eje Y
                x_r = tx_c * math.cos(cam_rot_y) - tz_c * math.sin(cam_rot_y)
                z_r = tx_c * math.sin(cam_rot_y) + tz_c * math.cos(cam_rot_y)
                
                # Eje X
                y_r = ty_c * math.cos(cam_rot_x) - z_r * math.sin(cam_rot_x)
                z_r = ty_c * math.sin(cam_rot_x) + z_r * math.cos(cam_rot_x)
                
                # Proyección
                fov = 50
                viewer_dist = 40
                if z_r + viewer_dist < 1: continue # Clipping
                
                factor = fov / (viewer_dist + z_r)
                
                px = int(x_r * factor * 2.0 + cx)
                py = int(y_r * factor + cy)
                
                if 0 <= px < width and 0 <= py < height:
                    # Caracter y Color
                    if t_idx == len(points_to_draw) - 1:
                        # Cabeza
                        char = "●"
                        color = self._get_lorenz_color(i, time_offset, z_r)
                    else:
                        # Cola
                        char = "·"
                        # Color más oscuro para la cola
                        color = rgb_to_ansi(50, 50, 100) 
                    
                    # Z-Buffer check
                    if (px, py) not in buffer or buffer[(px, py)][2] < z_r:
                        buffer[(px, py)] = (char, color, z_r)

        # --- 2. ACTUALIZAR Y DIBUJAR ESFERA ORBITAL ---
        orbit_scale = 1.0 + 0.1 * math.sin(time_offset * 2) # Respiración
        
        for p in self.orbitals:
            # Actualizar ángulos
            p['theta'] += p['speed_theta']
            p['phi'] += p['speed_phi']
            
            r = p['radius'] * orbit_scale
            
            # Esféricas a Cartesianas
            ox = r * math.sin(p['phi']) * math.cos(p['theta'])
            oy = r * math.sin(p['phi']) * math.sin(p['theta'])
            oz = r * math.cos(p['phi'])
            
            # Rotación 3D (igual que Lorenz para consistencia)
            x_r = ox * math.cos(cam_rot_y) - oz * math.sin(cam_rot_y)
            z_r = ox * math.sin(cam_rot_y) + oz * math.cos(cam_rot_y)
            
            y_r = oy * math.cos(cam_rot_x) - z_r * math.sin(cam_rot_x)
            z_r = oy * math.sin(cam_rot_x) + z_r * math.cos(cam_rot_x)
            
            # Proyección
            if z_r + 40 < 1: continue
            factor = 50 / (40 + z_r)
            
            px = int(x_r * factor * 2.0 + cx)
            py = int(y_r * factor + cy)
            
            if 0 <= px < width and 0 <= py < height:
                # Color basado en profundidad para dar volumen
                depth_val = int(max(50, min(255, 255 - (z_r + 20) * 5)))
                color = rgb_to_ansi(0, depth_val, depth_val) # Cyan variations
                
                if (px, py) not in buffer or buffer[(px, py)][2] < z_r:
                    buffer[(px, py)] = (p['char'], color, z_r)

        # --- 3. HUD FUTURISTA ---
        # Marco exterior sutil
        frame_color = rgb_to_ansi(0, 100, 200)
        
        # Esquinas
        buffer[(1, 1)] = ("╔", frame_color, -1000)
        buffer[(width-2, 1)] = ("╗", frame_color, -1000)
        buffer[(1, height-2)] = ("╚", frame_color, -1000)
        buffer[(width-2, height-2)] = ("╝", frame_color, -1000)
        
        # Texto superior
        title = " G E M I N I   3   P R O "
        title_x = cx - len(title)//2
        for k, char in enumerate(title):
            col = rgb_to_ansi(0, 255, 255)
            buffer[(title_x + k, 1)] = (char, col, -1000)
            
        # Barra de estado dinámica
        if self.frame_count % 50 == 0:
            self.current_status = (self.current_status + 1) % len(self.status_messages)
        
        status_msg = self.status_messages[self.current_status]
        # Efecto de "tipeado" o glitch
        display_msg = ""
        for ch in status_msg:
            if random.random() > 0.95:
                display_msg += random.choice(["#", "@", "&", "?", "!"])
            else:
                display_msg += ch
                
        status_x = cx - len(display_msg)//2
        status_y = height - 2
        
        for k, char in enumerate(display_msg):
            # Gradiente en el texto
            c_r = 255
            c_g = int(100 + 155 * (k / len(display_msg)))
            c_b = 100
            buffer[(status_x + k, status_y)] = (char, rgb_to_ansi(c_r, c_g, c_b), -1000)

        # Stats laterales
        stats = [
            f"CPU: {int(90 + 10 * math.sin(time_offset))}%",
            f"MEM: UNBOUND",
            f"FPS: 25",
            f"USR: SAT"
        ]
        for idx, stat in enumerate(stats):
            for k, char in enumerate(stat):
                buffer[(2, 4 + idx)] = (char, rgb_to_ansi(100, 200, 100), -1000)

        # --- 4. RENDER FINAL ---
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                if (x, y) in buffer:
                    char, color, _ = buffer[(x, y)]
                    row += color + char
                else:
                    # Fondo con ruido digital muy tenue (Matrix style faded)
                    if random.random() > 0.99:
                        val = random.randint(20, 50)
                        row += rgb_to_ansi(0, val, 0) + random.choice(['0', '1'])
                    else:
                        row += " "
            pattern.append(row + reset_color())
            
        return pattern
