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
        "version": "1.0",
        "description": "Fonda SmartUp celebra las Fiestas Patrias chilenas con tecnología y tradición"
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

        # Inicializar elementos
        self.fireworks = []
        self.empanadas = []
        self.tech_elements = []
        self.smartup_logos = []

        # Crear empanadas flotantes
        for _ in range(6):
            self.empanadas.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(0.3, 0.8),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.1, 0.3)
            })

        # Crear elementos tecnológicos (código, chips, etc.)
        for _ in range(10):
            self.tech_elements.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(0.1, 0.9),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.5, 1.5),
                'type': random.choice(['code', 'chip', 'wifi', 'data'])
            })

        # Crear logos SmartUp flotantes
        for _ in range(3):
            self.smartup_logos.append({
                'x': random.uniform(0.1, 0.9),
                'y': random.uniform(0.2, 0.8),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.2, 0.5)
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
            chars = ["</>", "{}", "[]", "0x", ">>", "&&", "||", "=="]
            return random.choice(chars)
        elif elem['type'] == 'chip':
            return "▢" if int(time_offset * 3) % 2 == 0 else "▣"
        elif elem['type'] == 'wifi':
            return "📶" if int(time_offset * 2) % 2 == 0 else "📡"
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

        # Fondo de estrellas digitales
        for _ in range(width * height // 60):  # Algunas estrellas de fondo
            x = random.randint(0, width-1)
            y = random.randint(0, height//2)  # Solo en la parte superior
            if random.random() < 0.4:
                canvas[y][x] = "·" if random.random() < 0.5 else "+"
                colors[y][x] = self.white

        # Crear nuevos fuegos artificiales
        self.create_firework(time_offset)

        # Limpiar fuegos artificiales viejos
        self.fireworks = [fw for fw in self.fireworks
                         if time_offset - fw['birth_time'] < 4]

        # Dibujar fuegos artificiales
        for fw in self.fireworks:
            pixels = self.draw_firework(fw, width, height, time_offset)
            for px, py, color, char in pixels:
                if 0 <= py < height and 0 <= px < width:
                    canvas[py][px] = char
                    colors[py][px] = color

        # TEXTO PRINCIPAL SIEMPRE VISIBLE
        # Mostrar "FONDA SMARTUP" 80% del tiempo y "¡VIVA CHILE!" 20% del tiempo
        show_viva_chile = int(time_offset * 0.2) % 10 == 0  # Solo 1 de cada 10 frames

        # Determinar qué texto mostrar basado en el tamaño de pantalla
        if width >= 90:
            if show_viva_chile:
                # VIVA CHILE - ASCII grande
                big_text = [
                    "██╗   ██╗██╗██╗   ██╗ █████╗ ",
                    "██║   ██║██║██║   ██║██╔══██╗",
                    "██║   ██║██║██║   ██║███████║",
                    "╚██╗ ██╔╝██║╚██╗ ██╔╝██╔══██║",
                    " ╚████╔╝ ██║ ╚████╔╝ ██║  ██║",
                    "  ╚═══╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝",
                    "",
                    "   ██████╗██╗  ██╗██╗██╗     ███████╗ ██╗",
                    "  ██╔════╝██║  ██║██║██║     ██╔════╝ ██║",
                    "  ██║     ███████║██║██║     █████╗   ██║",
                    "  ██║     ██╔══██║██║██║     ██╔══╝   ╚═╝",
                    "  ╚██████╗██║  ██║██║███████╗███████╗ ██╗",
                    "   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝ ╚═╝"
                ]
                text_color_type = "viva_chile"
            else:
                # FONDA SMARTUP - ASCII grande
                big_text = [
                    "███████╗ ██████╗ ███╗   ██╗██████╗  █████╗ ",
                    "██╔════╝██╔═══██╗████╗  ██║██╔══██╗██╔══██╗",
                    "█████╗  ██║   ██║██╔██╗ ██║██║  ██║███████║",
                    "██╔══╝  ██║   ██║██║╚██╗██║██║  ██║██╔══██║",
                    "██║     ╚██████╔╝██║ ╚████║██████╔╝██║  ██║",
                    "╚═╝      ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝",
                    "",
                    "███████╗███╗   ███╗ █████╗ ██████╗ ████████╗██╗   ██╗██████╗ ",
                    "██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝██║   ██║██╔══██╗",
                    "███████╗██╔████╔██║███████║██████╔╝   ██║   ██║   ██║██████╔╝",
                    "╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   ██║   ██║██╔═══╝ ",
                    "███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   ╚██████╔╝██║     ",
                    "╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝     "
                ]
                text_color_type = "fonda_smartup"
        elif width >= 50:
            if show_viva_chile:
                # VIVA CHILE - mediano
                big_text = [
                    "╦  ╦╦╦  ╦╔═╗",
                    "╚╗╔╝║╚╗╔╝╠═╣",
                    " ╚╝ ╩ ╚╝ ╩ ╩",
                    "",
                    "╔═╗╦ ╦╦╦  ╔═╗ ██╗",
                    "║  ╠═╣║║  ║╣  ██║",
                    "╚═╝╩ ╩╩╩═╝╚═╝ ╚═╝"
                ]
                text_color_type = "viva_chile"
            else:
                # FONDA SMARTUP - mediano
                big_text = [
                    "╔═╗╔═╗╔╗╔╔╦╗╔═╗",
                    "╠╣ ║ ║║║║ ║║╠═╣",
                    "╚  ╚═╝╝╚╝═╩╝╩ ╩",
                    "",
                    "╔═╗╔╦╗╔═╗╦═╗╔╦╗╦ ╦╔═╗",
                    "╚═╗║║║╠═╣╠╦╝ ║ ║ ║╠═╝",
                    "╚═╝╩ ╩╩ ╩╩╚═ ╩ ╚═╝╩  "
                ]
                text_color_type = "fonda_smartup"
        else:
            # Pantalla pequeña
            if show_viva_chile:
                big_text = [
                    "¡VIVA CHILE!",
                    "¡Fiestas Patrias!"
                ]
                text_color_type = "viva_chile"
            else:
                big_text = [
                    "FONDA SMARTUP",
                    "¡Tecnología + Tradición!"
                ]
                text_color_type = "fonda_smartup"

        # DIBUJAR EL TEXTO (siempre visible)
        start_y = max(2, height // 6)
        for line_idx, line in enumerate(big_text):
            text_y = start_y + line_idx
            if text_y < height and line.strip():  # Solo dibujar líneas no vacías
                text_x = max(0, width // 2 - len(line) // 2)
                for i, char in enumerate(line):
                    if text_x + i < width and char != ' ':
                        canvas[text_y][text_x + i] = char
                        # Aplicar colores según el tipo de texto
                        if text_color_type == "fonda_smartup":
                            colors[text_y][text_x + i] = self.tech_purple
                        else:  # viva_chile
                            if line_idx % 3 == 0:
                                colors[text_y][text_x + i] = self.red
                            elif line_idx % 3 == 1:
                                colors[text_y][text_x + i] = self.white
                            else:
                                colors[text_y][text_x + i] = self.blue

        # Dibujar empanadas flotantes con efectos digitales
        for emp in self.empanadas:
            # Movimiento flotante
            emp['x'] += emp['speed'] * 0.01 * math.sin(time_offset + emp['phase'])
            emp['y'] += 0.005 * math.cos(time_offset * 2 + emp['phase'])

            # Mantener en pantalla
            emp['x'] = emp['x'] % 1.0
            if emp['y'] < 0.1: emp['y'] = 0.1
            if emp['y'] > 0.9: emp['y'] = 0.9

            x = int(emp['x'] * width)
            y = int(emp['y'] * height)
            if 0 <= x < width and 0 <= y < height:
                # Empanadas con efectos digitales
                empanada_chars = ["🥟", "◢◣", "◤◥", "▰▱"]
                char_idx = int(time_offset * 2) % len(empanada_chars)
                char = empanada_chars[char_idx]
                if char == "🥟":
                    char = "◉"  # Fallback si no se soporta emoji
                canvas[y][x] = char
                colors[y][x] = self.orange

        # Dibujar elementos tecnológicos
        for tech in self.tech_elements:
            # Movimiento tecnológico
            tech['x'] += tech['speed'] * 0.005 * math.cos(time_offset + tech['phase'])
            tech['y'] += 0.003 * math.sin(time_offset * 1.5 + tech['phase'])

            # Mantener en pantalla
            tech['x'] = tech['x'] % 1.0
            tech['y'] = tech['y'] % 1.0

            x = int(tech['x'] * width)
            y = int(tech['y'] * height)
            if 0 <= x < width and 0 <= y < height:
                char = self.draw_tech_element(tech, x, y, time_offset)
                if len(char) > 1:  # Para strings como "</>", "{}", etc.
                    for i, c in enumerate(char):
                        if x + i < width:
                            canvas[y][x + i] = c
                            colors[y][x + i] = random.choice([self.blue, self.white])
                else:
                    canvas[y][x] = char
                    colors[y][x] = random.choice([self.blue, self.white])

        # Dibujar logos SmartUp flotantes
        for logo in self.smartup_logos:
            # Movimiento suave
            logo['phase'] += logo['speed'] * 0.1
            bounce = 0.03 * math.sin(logo['phase'])

            x = int(logo['x'] * width)
            y = int((logo['y'] + bounce) * height)

            if 0 <= x < width and 0 <= y < height:
                # Logo SmartUp como símbolo
                pose = int(logo['phase']) % 4
                if pose == 0:
                    char = "⚡"  # Rayo para tecnología
                elif pose == 1:
                    char = "🚀"  # Cohete para innovación
                elif pose == 2:
                    char = "💎"  # Diamante para calidad
                else:
                    char = "★"  # Estrella para excelencia

                # Fallbacks si no se soportan emojis
                if char == "⚡": char = "⚡" if width > 50 else "⚡"
                if char == "🚀": char = "▲"
                if char == "💎": char = "◆"

                canvas[y][x] = char
                colors[y][x] = random.choice([self.gold, self.red, self.blue])

        # Banderitas tecnológicas en la parte inferior
        banner_y = height - 3
        if banner_y > 0:
            for x in range(0, width, 8):
                if x < width:
                    canvas[banner_y][x] = "▲"
                    colors[banner_y][x] = self.blue if (x // 8) % 2 == 0 else self.red
                if x + 1 < width:
                    canvas[banner_y][x + 1] = "▲"
                    colors[banner_y][x + 1] = self.white
                if x + 2 < width:
                    canvas[banner_y][x + 2] = "◆"
                    colors[banner_y][x + 2] = self.red

        # Alternar mensaje en la parte inferior
        bottom_cycle = int(time_offset * 0.4) % 4  # Cambia cada 2.5 segundos
        if int(time_offset) % 12 < 4:  # Aparece cada 12 segundos por 4 segundos
            if bottom_cycle == 0:
                date_text = "FONDA SMARTUP 2024"
            elif bottom_cycle == 1:
                date_text = "18 DE SEPTIEMBRE"
            elif bottom_cycle == 2:
                date_text = "TECNOLOGÍA + TRADICIÓN"
            else:
                date_text = "¡VIVA CHILE DIGITAL!"

            date_x = max(0, width // 2 - len(date_text) // 2)
            date_y = height - 1
            if date_y > 0 and date_x >= 0:
                for i, char in enumerate(date_text):
                    if date_x + i < width:
                        canvas[date_y][date_x + i] = char
                        colors[date_y][date_x + i] = self.gold

        # Convertir canvas a strings
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                row += colors[y][x] + canvas[y][x]
            pattern.append(row + reset_color())

        return pattern