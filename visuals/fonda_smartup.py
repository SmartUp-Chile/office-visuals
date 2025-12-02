import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class FondaSmartUpVisual(VisualBase):
    """Fonda SmartUp celebra las Fiestas Patrias con elementos tecnológicos y tradición chilena"""

    metadata = {
        "name": "Fonda SmartUp",
        "author": "Manu",
        "version": "1.1",
        "description": "Fonda SmartUp celebra las Fiestas Patrias chilenas con tecnología y tradición",
        "ai_creator": "gpt-5-codex",
    }

    def __init__(self):
        # Colores patrios chilenos
        self.blue = rgb_to_ansi(0, 56, 147)     # Azul chileno
        self.red = rgb_to_ansi(217, 16, 35)     # Rojo chileno
        self.white = rgb_to_ansi(255, 255, 255) # Blanco
        self.gold = rgb_to_ansi(255, 215, 0)    # Dorado para efectos
        self.orange = rgb_to_ansi(255, 165, 0)  # Naranja para empanadas
        self.green = rgb_to_ansi(34, 139, 34)   # Verde para decoración
        self.yellow = rgb_to_ansi(255, 255, 0)  # Amarillo brillante
        self.tech_blue = rgb_to_ansi(0, 150, 255)  # Azul tecnológico
        self.tech_purple = rgb_to_ansi(150, 0, 255)  # Púrpura tecnológico

        # Inicializar elementos (modo CALM: casi estático)
        self.fireworks = []        # no usados en modo calm
        self.empanadas = []        # no usadas en modo calm
        self.tech_elements = []    # no usados en modo calm
        self.smartup_logos = []    # no usados en modo calm
        self.stars = []            # fondo de estrellas ESTÁTICAS (sin twinkle)
        self.kites = []            # volantines (animación suave)
        self.mountains = []        # montañas (estáticas)

        # Fuente 5x5 para título grande (ASCII ancho fijo)
        # X = píxel llenado, " " = vacío
        self.font5 = {
            'A': [
                " XXX ",
                "X   X",
                "XXXXX",
                "X   X",
                "X   X",
            ],
            'B': [
                "XXXX ",
                "X   X",
                "XXXX ",
                "X   X",
                "XXXX ",
            ],
            'C': [
                " XXX ",
                "X   X",
                "X    ",
                "X   X",
                " XXX ",
            ],
            'D': [
                "XXXX ",
                "X   X",
                "X   X",
                "X   X",
                "XXXX ",
            ],
            'E': [
                "XXXXX",
                "X    ",
                "XXXX ",
                "X    ",
                "XXXXX",
            ],
            'F': [
                "XXXXX",
                "X    ",
                "XXXX ",
                "X    ",
                "X    ",
            ],
            'H': [
                "X   X",
                "X   X",
                "XXXXX",
                "X   X",
                "X   X",
            ],
            'I': [
                "XXXXX",
                "  X  ",
                "  X  ",
                "  X  ",
                "XXXXX",
            ],
            'L': [
                "X    ",
                "X    ",
                "X    ",
                "X    ",
                "XXXXX",
            ],
            'M': [
                "X   X",
                "XX XX",
                "X X X",
                "X   X",
                "X   X",
            ],
            'N': [
                "X   X",
                "XX  X",
                "X X X",
                "X  XX",
                "X   X",
            ],
            'O': [
                " XXX ",
                "X   X",
                "X   X",
                "X   X",
                " XXX ",
            ],
            'P': [
                "XXXX ",
                "X   X",
                "XXXX ",
                "X    ",
                "X    ",
            ],
            'R': [
                "XXXX ",
                "X   X",
                "XXXX ",
                "X  X ",
                "X   X",
            ],
            'S': [
                " XXXX",
                "X    ",
                " XXX ",
                "    X",
                "XXXX ",
            ],
            'T': [
                "XXXXX",
                "  X  ",
                "  X  ",
                "  X  ",
                "  X  ",
            ],
            'U': [
                "X   X",
                "X   X",
                "X   X",
                "X   X",
                " XXX ",
            ],
            'V': [
                "X   X",
                "X   X",
                "X   X",
                " X X ",
                "  X  ",
            ],
            ' ': [
                "     ",
                "     ",
                "     ",
                "     ",
                "     ",
            ],
            '!': [
                "  X  ",
                "  X  ",
                "  X  ",
                "     ",
                "  X  ",
            ],
        }

        def sanitize(s: str) -> str:
            repl = str.maketrans({
                'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','Ü':'U','Ñ':'N',
                'á':'A','é':'E','í':'I','ó':'O','ú':'U','ü':'U','ñ':'N','¡':'!'
            })
            return s.translate(repl).upper()
        self._sanitize = sanitize

        def render_big(lines, width, height, colors, canvas, y_start, color_mode, time_offset):
            # Renderiza 5 filas por línea usando font5
            for li, text in enumerate(lines):
                text = self._sanitize(text)
                # Construir ancho total
                glyphs = [self.font5.get(ch, self.font5[' ']) for ch in text]
                glyph_width = sum(len(g[0]) for g in glyphs) + (len(glyphs)-1)  # 1 espacio entre glyphs
                x0 = max(0, width // 2 - glyph_width // 2)
                y0 = y_start + li*6  # 5 alto + 1 fila de espacio
                if y0+4 >= height:
                    break
                # Pintar filas
                x = x0
                for row in range(5):
                    colx = x
                    for idx, g in enumerate(glyphs):
                        row_data = g[row]
                        for cindex, ch in enumerate(row_data):
                            if ch != ' ' and 0 <= colx < width:
                                # Color
                                if color_mode == 'fonda_smartup':
                                    t = (colx - x0) / max(1, glyph_width-1)
                                    r = int(150 * (1 - t))
                                    gcol = int(150 * t)
                                    b = 255
                                    colors[y0+row][colx] = rgb_to_ansi(r, gcol, b)
                                else:
                                    band = int((colx + int(time_offset*2)) % 9)
                                    if band < 3:
                                        colors[y0+row][colx] = self.red
                                    elif band < 6:
                                        colors[y0+row][colx] = self.white
                                    else:
                                        colors[y0+row][colx] = self.blue
                                canvas[y0+row][colx] = '█'
                            colx += 1
                        # espacio entre glyphs
                        if idx < len(glyphs)-1:
                            if 0 <= colx < width:
                                canvas[y0+row][colx] = ' '
                            colx += 1
                    # siguiente fila ya se dibuja en la siguiente iteración
            # Devuelve el área ocupada para reservar
            total_height = len(lines)*6 - 1
            return glyph_width if lines else 0, total_height
        self._render_big = render_big

        # Crear estrellas estáticas (sin titileo)
        star_count = 160
        for _ in range(star_count):
            self.stars.append({
                'x': random.random(),
                'y': random.random() * 0.5,  # mitad superior
                'char': random.choice(['.', '+', '*'])
            })

        # Preparar volantines (kites) con posiciones ancladas y movimiento suave
        for i in range(4):
            self.kites.append({
                'x0': random.uniform(0.15, 0.85),
                'y0': random.uniform(0.15, 0.45),
                'ax': random.uniform(0.05, 0.12),
                'ay': random.uniform(0.03, 0.08),
                'phase': random.uniform(0, 2*math.pi),
                'speed': random.uniform(0.15, 0.28),
                'color': random.choice(['red','blue','white'])
            })

        # Montañas: define picos base (estáticos)
        self.mountains = []
        # Tres picos principales repartidos a lo ancho (alturas relativas)
        for px in [0.15, 0.5, 0.85]:
            self.mountains.append({
                'cx': px,               # centro relativo [0-1]
                'w': random.uniform(0.18, 0.28),  # anchura relativa
                'h': random.uniform(0.15, 0.22)   # altura relativa
            })

    def create_firework(self, time_offset):
        """Crear fuegos artificiales digitales"""
        if random.random() < 0.3:  # 30% chance cada frame
            self.fireworks.append({
                'x': random.uniform(0.1, 0.9),
                'y': random.uniform(0.1, 0.5),
                'birth_time': time_offset,
                'color': random.choice([self.red, self.blue, self.tech_blue, self.tech_purple]),
                'size': random.uniform(4, 10),
                'type': random.choice(['digital_burst', 'data_rain', 'pixel_explosion'])
            })

    def draw_tech_element(self, elem, x, y, time_offset):
        """Dibuja elementos tecnológicos"""
        if elem['type'] == 'code':
            # Solo caracteres de ancho fijo para evitar jitter
            chars = ["<>", "{}", "[]", "::", "==", "++", "--"]
            return random.choice(chars)
        elif elem['type'] == 'chip':
            return "▢" if int(time_offset * 3) % 2 == 0 else "▣"
        elif elem['type'] == 'wifi':
            # Evitar emojis variables; usar curvas ASCII
            return ")(" if int(time_offset * 2) % 2 == 0 else "/\\"
        elif elem['type'] == 'data':
            return "◆" if int(time_offset * 4) % 2 == 0 else "◇"
        return "●"

    def draw_firework(self, fw, width, height, time_offset):
        """Dibuja fuegos artificiales digitales"""
        age = time_offset - fw['birth_time']
        if age > 4:  # Los fuegos artificiales duran 4 segundos
            return []

        pixels = []
        cx = int(fw['x'] * width)
        cy = int(fw['y'] * height)

        if fw['type'] == 'digital_burst':
            # Explosión digital con píxeles
            radius = int(fw['size'] * age)
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                x = cx + int(radius * math.cos(rad))
                y = cy + int(radius * math.sin(rad))
                if 0 <= x < width and 0 <= y < height:
                    intensity = max(0, 1 - age/4)
                    if intensity > 0.7:
                        char = "█"
                    elif intensity > 0.4:
                        char = "▓"
                    elif intensity > 0.2:
                        char = "▒"
                    else:
                        char = "░"
                    pixels.append((x, y, fw['color'], char))

        elif fw['type'] == 'data_rain':
            # Lluvia de datos
            for i in range(int(fw['size'])):
                x = cx + random.randint(-5, 5)
                y = cy + int(age * 8) + i
                if 0 <= x < width and 0 <= y < height:
                    chars = ["1", "0", "▪", "▫", "•"]
                    char = random.choice(chars)
                    pixels.append((x, y, fw['color'], char))

        elif fw['type'] == 'pixel_explosion':
            # Explosión de píxeles
            for i in range(int(fw['size'] * 6)):
                angle = random.uniform(0, 2 * math.pi)
                r = random.uniform(0, fw['size'] * age)
                x = cx + int(r * math.cos(angle))
                y = cy + int(r * math.sin(angle))
                if 0 <= x < width and 0 <= y < height:
                    pixels.append((x, y, fw['color'], "◼"))

        return pixels

    def generate_frame(self, width, height, time_offset):
        # Crear matriz de caracteres
        canvas = [[" " for _ in range(width)] for _ in range(height)]
        colors = [["" for _ in range(width)] for _ in range(height)]

        # Texto fijo (sin alternancia para cero jitter)
        text_lines = ["FONDA SMARTUP"]
        start_y = max(2, height // 8)
        # Zona de exclusión amplia del título
        pad = 2
        approx_width = int(width*0.9)
        rx1 = max(0, (width - approx_width)//2 - pad)
        rx2 = min(width - 1, (width + approx_width)//2 + pad)
        ry1 = max(0, start_y - 1)
        ry2 = min(height - 1, start_y + 6*len(text_lines))

        # Fondo de estrellas digitales (ESTÁTICAS, sin cambio de frame)
        for s in self.stars:
            sx = int(s['x'] * width)
            sy = int(s['y'] * height)
            if 0 <= sx < width and 0 <= sy < height:
                canvas[sy][sx] = s['char']
                colors[sy][sx] = self.white

        # Utilidades locales para detalle estático y determinista (sin jitter)
        def hhash(a, b):
            v = (a * 374761393 + b * 668265263) & 0xFFFFFFFF
            v ^= (v >> 13)
            v = (v * 1274126177) & 0xFFFFFFFF
            return v
        def n01(a, b):
            return (hhash(a, b) / 0xFFFFFFFF)
        def draw_triangle_mountain(cx, base_y, peak_y, half_w, front=True):
            height_px = max(1, base_y - peak_y)
            for y in range(peak_y, base_y + 1):
                t = (y - peak_y) / height_px
                hw = int(half_w * t)
                # nieve en el 12-18% superior
                snow = t < 0.18
                for x in range(cx - hw, cx + hw + 1):
                    if not (0 <= x < width):
                        continue
                    # no excluimos área de texto: queremos fondo detrás de las letras
                    # texturizado según altura y hash estable
                    r = n01(x, y)
                    if snow:
                        ch = '▓' if r > 0.7 else '█'
                        col = self.white
                    else:
                        # roca: dither por altura
                        if t < 0.45:
                            ch = '▓' if r > 0.5 else '█'
                            shade = 190 - int(50*t)
                        elif t < 0.75:
                            ch = '▒' if r > 0.35 else '▓'
                            shade = 160 - int(40*(t-0.45)/0.3)
                        else:
                            ch = '░' if r > 0.25 else '▒'
                            shade = 130 - int(30*(t-0.75)/0.25)
                        shade = max(60, min(220, shade))
                        col = rgb_to_ansi(shade, shade, shade)
                    canvas[y][x] = ch
                    colors[y][x] = col

                # aristas: remarcar bordes con líneas sutiles
                left = cx - hw
                right = cx + hw
                if 0 <= left < width:
                    colors[y][left] = rgb_to_ansi(100, 100, 100)
                    canvas[y][left] = '/' if front else '/'
                if 0 <= right < width:
                    colors[y][right] = rgb_to_ansi(100, 100, 100)
                    canvas[y][right] = '\\' if front else '\\'

        # Montañas en dos planos: fondo (más claro) y frente (más oscuro)
        flag_h = 6
        # Extiende la montaña hasta el fondo; las banderas se dibujan encima después
        base_y = height - 1
        # Fondo: picos más anchos y altos (suben más), color más claro
        for m in self.mountains:
            cx = int(m['cx'] * width)
            half_w = max(3, int((m['w'] * width)))  # ancho fondo
            peak_y = max(0, base_y - int(height * (0.40 + 0.10 * (m['h'] / 0.22))))
            draw_triangle_mountain(cx, base_y, peak_y, half_w, front=False)
        # Frente: picos definidos (más altos aún)
        for m in self.mountains:
            cx = int(m['cx'] * width)
            half_w = max(2, int((m['w'] * width) * 0.6))
            peak_y = max(0, base_y - int(height * (0.55 + 0.12 * (m['h'] / 0.22))))
            draw_triangle_mountain(cx, base_y, peak_y, half_w, front=True)

        # Modo calm: sin fuegos, sin elementos móviles.

        # Texto a usar (bloque grande, colores estáticos)
        big_text = text_lines
        text_color_type = "fonda_smartup"

        # Dibuja el texto ANTES de kites para que los volantines pasen por encima
        self._render_big(big_text, width, height, colors, canvas, start_y, text_color_type, time_offset)

        # (El texto se dibuja como overlay al final para máxima estabilidad)

        # Dibujar empanadas flotantes con efectos digitales
        for emp in self.empanadas:
            # Movimiento flotante
            emp['x'] += emp['speed'] * 0.008 * math.sin(time_offset * 0.8 + emp['phase'])
            emp['y'] += 0.0035 * math.cos(time_offset * 1.2 + emp['phase'])

            # Mantener en pantalla
            emp['x'] = emp['x'] % 1.0
            if emp['y'] < 0.1: emp['y'] = 0.1
            if emp['y'] > 0.9: emp['y'] = 0.9

            x = int(emp['x'] * width)
            y = int(emp['y'] * height)
            if 0 <= x < width and 0 <= y < height:
                # Empanadas con efectos digitales
                empanada_chars = ["◢◣", "◤◥", "▰▱", "◧◨"]
                char_idx = int(time_offset * 2) % len(empanada_chars)
                char = empanada_chars[char_idx]
                if not (rx1 <= x <= rx2 and ry1 <= y <= ry2):
                    canvas[y][x] = char
                    colors[y][x] = self.orange

        # Dibujar elementos tecnológicos
        for tech in self.tech_elements:
            # Movimiento tecnológico
            tech['x'] += tech['speed'] * 0.004 * math.cos(time_offset * 0.9 + tech['phase'])
            tech['y'] += 0.0025 * math.sin(time_offset * 1.1 + tech['phase'])

            # Mantener en pantalla
            tech['x'] = tech['x'] % 1.0
            tech['y'] = tech['y'] % 1.0

            x = int(tech['x'] * width)
            y = int(tech['y'] * height)
            if 0 <= x < width and 0 <= y < height:
                char = self.draw_tech_element(tech, x, y, time_offset)
                if len(char) > 1:  # Para strings como "<>", "{}", etc.
                    for i, c in enumerate(char):
                        if x + i < width:
                            if not (rx1 <= x + i <= rx2 and ry1 <= y <= ry2):
                                canvas[y][x + i] = c
                                colors[y][x + i] = random.choice([self.blue, self.white])
                else:
                    if not (rx1 <= x <= rx2 and ry1 <= y <= ry2):
                        canvas[y][x] = char
                        colors[y][x] = random.choice([self.blue, self.white])

        # Dibujar logos SmartUp flotantes
        for logo in self.smartup_logos:
            # Movimiento suave
            logo['phase'] += logo['speed'] * 0.08
            bounce = 0.02 * math.sin(logo['phase'])

            x = int(logo['x'] * width)
            y = int((logo['y'] + bounce) * height)

            if 0 <= x < width and 0 <= y < height:
                # Logo SmartUp como símbolo (solo ASCII ancho fijo)
                pose = int(logo['phase']) % 4
                chars = ["★", "▲", "◆", "+"]
                char = chars[pose]

                if not (rx1 <= x <= rx2 and ry1 <= y <= ry2):
                    canvas[y][x] = char
                    colors[y][x] = random.choice([self.gold, self.red, self.blue])

        # Mini-banderas de Chile (más piolas): solo 3 a lo ancho
        flag_h = 6
        flag_top = height - flag_h
        if flag_top >= 0:
            positions = [int(width*0.15), int(width*0.5), int(width*0.85)]
            tile_w = 12
            canton_w = 5
            half_h = flag_h // 2
            for cx in positions:
                x0 = max(0, cx - tile_w//2)
                for dy in range(flag_h):
                    y = flag_top + dy
                    if y < 0 or y >= height:
                        continue
                    for dx in range(tile_w):
                        x = x0 + dx
                        if x >= width:
                            break
                        if dy < half_h:
                            if dx < canton_w:
                                canvas[y][x] = '█'
                                colors[y][x] = self.blue
                                if dy == 1 and dx == 2:
                                    canvas[y][x] = '*'
                                    colors[y][x] = self.white
                            else:
                                canvas[y][x] = '█'
                                colors[y][x] = self.white
                        else:
                            canvas[y][x] = '█'
                            colors[y][x] = self.red

        # Sutileza animada: un destello dorado recorre la última fila lentamente
        # (no afecta texto ni geometría, sólo un punto que se desplaza)
        if height > 0 and width > 0:
            trail_y = height - 1
            spark_x = int((time_offset * 0.5)) % max(1, width)  # muy lento
            canvas[trail_y][spark_x] = '•'
            colors[trail_y][spark_x] = self.gold

        # Mensaje inferior ESTÁTICO
        date_text = "FONDA SMARTUP 2024"
        date_x = max(0, width // 2 - len(date_text) // 2)
        date_y = height - 1
        if date_y > 0 and date_x >= 0:
            for i, char in enumerate(date_text):
                if date_x + i < width:
                    canvas[date_y][date_x + i] = char
                    colors[date_y][date_x + i] = self.gold

        # Volantines (kites) animados suavemente (rombos 5x5 + cuerda curvada)
        for k in self.kites:
            # centro con oscilación leve
            x = k['x0'] + k['ax'] * math.sin(time_offset * k['speed'] + k['phase'])
            y = k['y0'] + k['ay'] * math.sin(time_offset * k['speed'] * 0.9 + k['phase']*0.7)
            angle = 0.25 * math.sin(time_offset * k['speed'] * 0.6 + k['phase'])  # rotación suave
            scale = 2 + (1 if width > 100 else 0)
            cx = int(x * width)
            cy = int(y * height)
            # dibujar rombo relleno
            col = self.red if k['color']=='red' else self.blue if k['color']=='blue' else self.white
            for dy in range(-2*scale, 2*scale+1):
                for dx in range(-2*scale, 2*scale+1):
                    # rotación del vector
                    rx = int(dx*math.cos(angle) - dy*math.sin(angle))
                    ry = int(dx*math.sin(angle) + dy*math.cos(angle))
                    # condición de rombo |rx| + |ry| <= 2*scale
                    if abs(rx) + abs(ry) <= 2*scale:
                        xx = cx + dx
                        yy = cy + dy
                        if 0 <= xx < width and 0 <= yy < height:
                            # detalle: borde más brillante
                            if abs(rx) + abs(ry) == 2*scale:
                                ch = '◆'
                            else:
                                # trama interna
                                ch = '▓' if ((rx + 3*ry) % 3 == 0) else '▒'
                            canvas[yy][xx] = ch
                            colors[yy][xx] = col
            # cuerda curvada hacia abajo
            # cola mucho más larga (alcanza más cerca del pie)
            tail_len = min(max(16, int(height * 0.75)), max(0, height - cy - 2))
            for i in range(1, tail_len+1):
                tx = cx - int(i * 0.8) + int(2*math.sin(i*0.7 + time_offset*0.2))
                ty = cy + i
                if 0 <= tx < width and 0 <= ty < height:
                    canvas[ty][tx] = '~' if i % 2 == 0 else '-'
                    colors[ty][tx] = col

        # (Texto ya dibujado antes de los kites para permitir que los kites pasen por encima)

        # Convertir canvas a strings
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                row += colors[y][x] + canvas[y][x]
            pattern.append(row + reset_color())

        return pattern
