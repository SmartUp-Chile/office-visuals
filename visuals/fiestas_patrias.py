import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color

class FiestasPatriasVisual(VisualBase):
    """Celebración de Fiestas Patrias Chilenas con fuegos artificiales, empanadas y elementos festivos"""

    metadata = {
        "name": "Fiestas Patrias Chile",
        "author": "Manu",
        "version": "1.0",
        "description": "Celebración chilena con fuegos artificiales, empanadas y baile cueca"
    }

    def __init__(self):
        # Colores patrios chilenos
        self.blue = rgb_to_ansi(0, 56, 147)     # Azul chileno
        self.red = rgb_to_ansi(217, 16, 35)     # Rojo chileno
        self.white = rgb_to_ansi(255, 255, 255) # Blanco
        self.gold = rgb_to_ansi(255, 215, 0)    # Dorado para fuegos artificiales
        self.orange = rgb_to_ansi(255, 165, 0)  # Naranja para empanadas
        self.green = rgb_to_ansi(34, 139, 34)   # Verde para decoración
        self.yellow = rgb_to_ansi(255, 255, 0)  # Amarillo brillante

        # Inicializar fuegos artificiales
        self.fireworks = []
        self.empanadas = []
        self.dancers = []

        # Crear algunas empanadas flotantes
        for _ in range(8):
            self.empanadas.append({
                'x': random.uniform(0, 1),
                'y': random.uniform(0.3, 0.8),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(0.1, 0.3)
            })

        # Crear bailarines de cueca
        for _ in range(4):
            self.dancers.append({
                'x': random.uniform(0.2, 0.8),
                'y': random.uniform(0.7, 0.9),
                'phase': random.uniform(0, 2 * math.pi),
                'speed': random.uniform(1, 2)
            })

    def create_firework(self, time_offset):
        """Crear fuegos artificiales aleatorios"""
        if random.random() < 0.25:  # 25% chance cada frame - más fuegos artificiales
            self.fireworks.append({
                'x': random.uniform(0.1, 0.9),
                'y': random.uniform(0.1, 0.5),
                'birth_time': time_offset,
                'color': random.choice([self.red, self.blue, self.white]),
                'size': random.uniform(3, 8),
                'type': random.choice(['burst', 'cascade', 'spiral'])
            })

    def draw_empanada(self, x, y):
        """Dibuja una empanada en posición específica"""
        return "🥟"  # Si no funciona unicode, usar "◐"

    def draw_firework(self, fw, width, height, time_offset):
        """Dibuja un fuego artificial"""
        age = time_offset - fw['birth_time']
        if age > 3:  # Los fuegos artificiales duran 3 segundos
            return []

        pixels = []
        cx = int(fw['x'] * width)
        cy = int(fw['y'] * height)

        if fw['type'] == 'burst':
            # Explosión circular
            radius = int(fw['size'] * age)
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                x = cx + int(radius * math.cos(rad))
                y = cy + int(radius * math.sin(rad))
                if 0 <= x < width and 0 <= y < height:
                    intensity = max(0, 1 - age/3)  # Fade out
                    pixels.append((x, y, fw['color'], "✦" if intensity > 0.5 else "·"))

        elif fw['type'] == 'cascade':
            # Cascada hacia abajo
            for i in range(int(fw['size'])):
                x = cx + random.randint(-3, 3)
                y = cy + int(age * 5) + i
                if 0 <= x < width and 0 <= y < height:
                    pixels.append((x, y, fw['color'], "✦" if age < 1 else "·"))

        elif fw['type'] == 'spiral':
            # Espiral
            for i in range(int(fw['size'] * 4)):
                angle = i * 0.5 + time_offset * 3
                r = i * age
                x = cx + int(r * math.cos(angle))
                y = cy + int(r * math.sin(angle))
                if 0 <= x < width and 0 <= y < height:
                    pixels.append((x, y, fw['color'], "★"))

        return pixels

    def draw_chilean_flag(self, canvas, colors, width, height):
        """Dibuja una bandera chilena ASCII en la esquina superior derecha"""
        # ASCII art de bandera chilena más detallada
        flag_lines = [
            "┌────────────────┐",
            "│████████░░░░░░░░│",
            "│████████░░░░░░░░│",
            "│██★█████░░░░░░░░│",
            "│████████░░░░░░░░│",
            "│████████░░░░░░░░│",
            "│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│",
            "│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│",
            "│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│",
            "│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│",
            "└────────────────┘"
        ]

        start_x = width - 20
        start_y = 1

        if start_x > 0:
            for i, line in enumerate(flag_lines):
                fy = start_y + i
                if fy < height:
                    for j, char in enumerate(line):
                        fx = start_x + j
                        if fx < width:
                            canvas[fy][fx] = char
                            # Colorear según el carácter
                            if char == '█':
                                colors[fy][fx] = self.blue
                            elif char == '★':
                                colors[fy][fx] = self.white
                            elif char == '░':
                                colors[fy][fx] = self.white
                            elif char == '▓':
                                colors[fy][fx] = self.red
                            else:
                                colors[fy][fx] = self.white

    def generate_frame(self, width, height, time_offset):
        # Crear matriz de caracteres
        canvas = [[" " for _ in range(width)] for _ in range(height)]
        colors = [["" for _ in range(width)] for _ in range(height)]

        # Fondo estrellado
        for _ in range(width * height // 50):  # Algunas estrellas de fondo
            x = random.randint(0, width-1)
            y = random.randint(0, height//2)  # Solo en la parte superior
            if random.random() < 0.3:
                canvas[y][x] = "·"
                colors[y][x] = self.white

        # Crear nuevos fuegos artificiales
        self.create_firework(time_offset)

        # Limpiar fuegos artificiales viejos
        self.fireworks = [fw for fw in self.fireworks
                         if time_offset - fw['birth_time'] < 3]

        # Dibujar fuegos artificiales
        for fw in self.fireworks:
            pixels = self.draw_firework(fw, width, height, time_offset)
            for px, py, color, char in pixels:
                if 0 <= py < height and 0 <= px < width:
                    canvas[py][px] = char
                    colors[py][px] = color


        # Texto "¡VIVA CHILE MIERDA!" grande que aparece ocasionalmente
        if int(time_offset * 2) % 8 < 3:  # Aparece 3/8 del tiempo
            # ASCII art para texto más grande
            big_text = [
                "██╗   ██╗██╗██╗   ██╗ █████╗     ██████╗██╗  ██╗██╗██╗     ███████╗",
                "██║   ██║██║██║   ██║██╔══██╗   ██╔════╝██║  ██║██║██║     ██╔════╝",
                "██║   ██║██║██║   ██║███████║   ██║     ███████║██║██║     █████╗  ",
                "╚██╗ ██╔╝██║╚██╗ ██╔╝██╔══██║   ██║     ██╔══██║██║██║     ██╔══╝  ",
                " ╚████╔╝ ██║ ╚████╔╝ ██║  ██║   ╚██████╗██║  ██║██║███████╗███████╗",
                "  ╚═══╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝",
                "                    ███╗   ███╗██╗███████╗██████╗ ██████╗  █████╗ ██╗",
                "                    ████╗ ████║██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██║",
                "                    ██╔████╔██║██║█████╗  ██████╔╝██║  ██║███████║██║",
                "                    ██║╚██╔╝██║██║██╔══╝  ██╔══██╗██║  ██║██╔══██║╚═╝",
                "                    ██║ ╚═╝ ██║██║███████╗██║  ██║██████╔╝██║  ██║██╗",
                "                    ╚═╝     ╚═╝╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝"
            ]

            # Si el texto es muy grande, usar versión más simple
            if width < 90:
                big_text = [
                    "╦  ╦╦╦  ╦╔═╗  ╔═╗╦ ╦╦╦  ╔═╗",
                    "╚╗╔╝║╚╗╔╝╠═╣  ║  ╠═╣║║  ║╣ ",
                    " ╚╝ ╩ ╚╝ ╩ ╩  ╚═╝╩ ╩╩╩═╝╚═╝",
                    "   ╔╦╗╦╔═╗╦═╗╔╦╗╔═╗ ██╗",
                    "   ║║║║║╣ ╠╦╝ ║║╠═╣ ██║",
                    "   ╩ ╩╩╚═╝╩╚══╩╝╩ ╩ ╚═╝"
                ]

            # Si es aún más pequeño, usar texto normal pero duplicado
            if width < 50:
                big_text = [
                    "¡¡VIVA CHILE MIERDA!!",
                    "¡¡VIVA CHILE MIERDA!!"
                ]

            # Centrar y dibujar el texto
            start_y = height // 8
            for line_idx, line in enumerate(big_text):
                text_y = start_y + line_idx
                if text_y < height:
                    text_x = max(0, width // 2 - len(line) // 2)
                    for i, char in enumerate(line):
                        if text_x + i < width and char != ' ':
                            canvas[text_y][text_x + i] = char
                            # Colores alternos por línea
                            if line_idx % 3 == 0:
                                colors[text_y][text_x + i] = self.red
                            elif line_idx % 3 == 1:
                                colors[text_y][text_x + i] = self.white
                            else:
                                colors[text_y][text_x + i] = self.blue

        # Dibujar empanadas flotantes
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
                # ASCII empanada más visible
                empanada_chars = ["◢◣", "◤◥", "▰▱", "◉◎"]
                char = empanada_chars[int(time_offset * 2) % len(empanada_chars)]
                canvas[y][x] = char[0] if x % 2 == 0 else char[1]
                colors[y][x] = self.orange

        # Dibujar bailarines (representados como figuras simples)
        for dancer in self.dancers:
            # Movimiento de baile
            dancer['phase'] += dancer['speed'] * 0.1
            bounce = 0.02 * math.sin(dancer['phase'] * 2)

            x = int(dancer['x'] * width)
            y = int((dancer['y'] + bounce) * height)

            if 0 <= x < width and 0 <= y < height:
                # Bailarines ASCII más visibles
                pose = int(dancer['phase']) % 6
                if pose == 0:
                    char = "♀"  # Mujer bailando
                elif pose == 1:
                    char = "♂"  # Hombre bailando
                elif pose == 2:
                    char = "◉"  # Persona saltando
                elif pose == 3:
                    char = "☺"  # Cara feliz
                elif pose == 4:
                    char = "☻"  # Cara feliz rellena
                else:
                    char = "♩"  # Nota musical

                canvas[y][x] = char
                colors[y][x] = random.choice([self.red, self.blue, self.white])

                # Agregar sombra o complemento al lado
                if x + 1 < width and canvas[y][x + 1] == " ":
                    canvas[y][x + 1] = "~"  # Movimiento
                    colors[y][x + 1] = colors[y][x]

        # Banderitas chilenas en la parte inferior
        banner_y = height - 3
        if banner_y > 0:
            for x in range(0, width, 6):
                if x < width:
                    canvas[banner_y][x] = "▲"
                    colors[banner_y][x] = self.red if (x // 6) % 2 == 0 else self.blue
                if x + 1 < width:
                    canvas[banner_y][x + 1] = "▲"
                    colors[banner_y][x + 1] = self.white

        # Crear mensaje "18 DE SEPTIEMBRE" ocasionalmente
        if int(time_offset) % 10 < 3:  # Aparece cada 10 segundos por 3 segundos
            date_text = "18 DE SEPTIEMBRE"
            date_x = width // 2 - len(date_text) // 2
            date_y = height - 1
            if date_y > 0 and date_x > 0:
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