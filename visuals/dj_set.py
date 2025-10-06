import math
import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class DJSetVisual(VisualBase):
    """Top-down DJ table: two spinning turntables, mixer with faders and knobs."""

    metadata = {
        "name": "DJ Set",
        "author": "DiesiOslo",
        "version": "2.0",
        "description": "Pro DJ booth: dual decks with screens, 4ch mixer, VU meters, pads, LEDs"
    }

    def __init__(self):
        # Animation state
        self.left_angle = 0.0
        self.right_angle = math.pi
        # Platter speeds modulated by pitch sliders
        self.left_speed = 0.12
        self.right_speed = 0.10
        self.left_pitch = 0.5   # 0-1 (down-up)
        self.right_pitch = 0.5  # 0-1
        # 4-channel mixer
        self.channel_count = 4
        self.faders = [0.3, 0.7, 0.5, 0.6]  # 0-1
        self.crossfader = 0.5               # 0 left, 1 right
        self.knobs = [0.2, 0.5, 0.8, 0.4, 0.65, 0.35, 0.55, 0.25]  # 8 knobs top
        self.vu_phases = [random.random() * 6.283 for _ in range(self.channel_count)]
        self.master_vu_phase = 0.0
        # Deck screens, pads, LEDs
        self.left_wave_phase = 0.0
        self.right_wave_phase = 1.7
        self.pad_phase = 0.0
        self.sparkle_phase = 0.0
        self.logo_pulse = 0.0

    def _draw_char(self, fb, cb, x, y, width, height, char, color):
        if 0 <= x < width and 0 <= y < height:
            fb[y][x] = char
            cb[y][x] = color

    def _disc_color(self, radius_norm, angle):
        # Subtle cyan/blue ring gradient
        hue_shift = (math.sin(angle * 6) * 0.5 + 0.5) * 40
        r = int(30 + 20 * (1 - radius_norm))
        g = int(120 + 80 * (1 - radius_norm))
        b = int(200 + hue_shift)
        return rgb_to_ansi(r, g, min(255, b))

    def _accent_color(self, t):
        # Magenta accent that pulses with time
        r = int(180 + 50 * math.sin(t))
        g = int(40 + 20 * math.sin(t * 0.5 + 1.7))
        b = int(220 + 35 * math.sin(t * 0.8 + 0.3))
        return rgb_to_ansi(min(255, r), max(0, g), min(255, b))

    def _panel_color(self):
        # Dark gray panel
        return rgb_to_ansi(80, 90, 110)

    def _draw_rect(self, fb, cb, x0, y0, x1, y1, char, color):
        if x0 > x1 or y0 > y1:
            return
        width = len(fb[0])
        height = len(fb)
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(width - 1, x1)
        y1 = min(height - 1, y1)
        for y in range(y0, y1 + 1):
            row_fb = fb[y]
            row_cb = cb[y]
            for x in range(x0, x1 + 1):
                row_fb[x] = char
                row_cb[x] = color

    def _vu_color(self, level_norm):
        # green -> yellow -> red based on level
        if level_norm < 0.6:
            frac = level_norm / 0.6
            r = int(40 + 50 * frac)
            g = int(170 + 70 * frac)
            b = 40
        elif level_norm < 0.85:
            frac = (level_norm - 0.6) / 0.25
            r = int(90 + 130 * frac)
            g = 240
            b = 40
        else:
            frac = (level_norm - 0.85) / 0.15
            r = 255
            g = int(240 - 150 * frac)
            b = int(40 + 40 * frac)
        return rgb_to_ansi(r, g, b)

    def _clamp(self, value, lo=0.0, hi=1.0):
        return max(lo, min(hi, value))

    def generate_frame(self, width, height, time_offset):
        # Update state
        # Pitch sliders oscillate slowly and modulate platter speed
        self.left_pitch = self._clamp(0.5 + 0.45 * math.sin(time_offset * 0.12))
        self.right_pitch = self._clamp(0.5 + 0.45 * math.sin(time_offset * 0.11 + 1.3))
        speed_left = self.left_speed * (0.7 + self.left_pitch * 0.6)
        speed_right = self.right_speed * (0.7 + self.right_pitch * 0.6)
        self.left_angle += speed_left
        self.right_angle -= speed_right
        self.left_wave_phase += 0.08 * (0.8 + self.left_pitch * 0.6)
        self.right_wave_phase += 0.08 * (0.8 + self.right_pitch * 0.6)
        self.sparkle_phase += 0.05
        self.logo_pulse += 0.05
        self.pad_phase += 0.1
        # Animate controls
        self.crossfader = (math.sin(time_offset * 0.25) * 0.5 + 0.5)
        for i in range(self.channel_count):
            phase = [0.4, 0.33, 0.29, 0.36][i]
            offset = [0.0, 1.2, 2.0, 2.7][i]
            self.faders[i] = self._clamp(math.sin(time_offset * phase + offset) * 0.5 + 0.5)
            self.vu_phases[i] += 0.12 + 0.03 * i
        for i in range(len(self.knobs)):
            self.knobs[i] = 0.5 + 0.45 * math.sin(time_offset * (0.22 + i * 0.06) + i)
        self.master_vu_phase += 0.1

        # Frame buffers
        fb = [[' ' for _ in range(width)] for _ in range(height)]
        cb = [['' for _ in range(width)] for _ in range(height)]

        # Layout
        cx_left = int(width * 0.22)
        cx_right = int(width * 0.78)
        cy = int(height * 0.56)
        platter_r = max(7, int(min(width, height) * 0.2))
        label_r = max(2, int(platter_r * 0.34))

        # Mixer area bounds (center block)
        mixer_x0 = int(width * 0.34)
        mixer_x1 = int(width * 0.66)
        mixer_y0 = int(height * 0.20)
        mixer_y1 = int(height * 0.86)

        panel_color = self._panel_color()

        # Draw deck panels (left/right) and subtle background texture
        deck_color = rgb_to_ansi(60, 65, 80)
        for y in range(1, height - 1, 4):
            for x in range(0, width):
                if random.random() < 0.04:
                    self._draw_char(fb, cb, x, y, width, height, '·', deck_color)

        deck_pad = 6
        left_panel_x0 = max(0, cx_left - platter_r - deck_pad)
        left_panel_x1 = min(width - 1, cx_left + platter_r + deck_pad)
        left_panel_y0 = max(0, cy - platter_r - deck_pad)
        left_panel_y1 = min(height - 1, cy + platter_r + deck_pad + 2)
        right_panel_x0 = max(0, cx_right - platter_r - deck_pad)
        right_panel_x1 = min(width - 1, cx_right + platter_r + deck_pad)
        right_panel_y0 = left_panel_y0
        right_panel_y1 = left_panel_y1
        self._draw_rect(fb, cb, left_panel_x0, left_panel_y0, left_panel_x1, left_panel_y1, '▒', rgb_to_ansi(45, 50, 65))
        self._draw_rect(fb, cb, right_panel_x0, right_panel_y0, right_panel_x1, right_panel_y1, '▒', rgb_to_ansi(45, 50, 65))

        # Draw mixer panel block
        self._draw_rect(fb, cb, mixer_x0, mixer_y0, mixer_x1, mixer_y1, '░', panel_color)
        # Screws on panels
        screw_color = rgb_to_ansi(160, 170, 190)
        for (x0, y0, x1, y1) in [
            (left_panel_x0, left_panel_y0, left_panel_x1, left_panel_y1),
            (right_panel_x0, right_panel_y0, right_panel_x1, right_panel_y1),
            (mixer_x0, mixer_y0, mixer_x1, mixer_y1)
        ]:
            for (sx, sy) in [(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)]:
                self._draw_char(fb, cb, sx, sy, width, height, '•', screw_color)

        # Helper to draw a platter
        def draw_platter(center_x, center_y, angle):
            for y in range(center_y - platter_r, center_y + platter_r + 1):
                for x in range(center_x - platter_r, center_x + platter_r + 1):
                    dx = x - center_x
                    dy = y - center_y
                    rr = math.sqrt(dx * dx + dy * dy)
                    if rr <= platter_r + 0.2:
                        rn = rr / platter_r
                        # ring structure
                        if rr <= label_r:
                            # inner label with slight pulse
                            pulse = (math.sin(angle * 2 + rr) * 0.5 + 0.5) * 25
                            color = rgb_to_ansi(220 + int(pulse), 220 + int(pulse), 230)
                            char = '●'
                        elif rr <= platter_r * 0.65:
                            color = self._disc_color(rn, angle)
                            # grooves
                            grooves = int(((rr - label_r) * 2 + math.sin(angle * 3 + rr * 0.4)) % 3)
                            char = ['·', '░', '▒'][grooves]
                        elif rr <= platter_r * 0.95:
                            color = self._disc_color(rn, angle)
                            char = '▓'
                        else:
                            # rim
                            rim_gloss = int(20 + 30 * (1 - rn))
                            color = rgb_to_ansi(200 + rim_gloss, 200 + rim_gloss, 230)
                            char = '█'
                        self._draw_char(fb, cb, x, y, width, height, char, color)

            # rotating marker on label
            mx = int(center_x + math.cos(angle) * (label_r - 1))
            my = int(center_y + math.sin(angle) * (label_r - 1))
            self._draw_char(fb, cb, mx, my, width, height, '◆', self._accent_color(time_offset * 2 + angle))

            # strobe dots around rim
            for k in range(18):
                a = angle + k * (2 * math.pi / 18)
                rx = int(center_x + math.cos(a) * (platter_r - 1))
                ry = int(center_y + math.sin(a) * (platter_r - 1))
                blink = (k + int(time_offset * 5)) % 4
                if blink == 0:
                    self._draw_char(fb, cb, rx, ry, width, height, '•', rgb_to_ansi(255, 200, 120))
                elif blink == 1:
                    self._draw_char(fb, cb, rx, ry, width, height, '·', rgb_to_ansi(200, 120, 60))

        # Draw both platters
        draw_platter(cx_left, cy, self.left_angle)
        draw_platter(cx_right, cy, self.right_angle)

        # Deck screens with waveform and progress
        def draw_deck_screen(center_x, top_y, width_chars, height_chars, phase, color_base):
            x0 = center_x - width_chars // 2
            y0 = top_y
            x1 = x0 + width_chars - 1
            y1 = y0 + height_chars - 1
            border_color = rgb_to_ansi(30, 200, 220)
            self._draw_rect(fb, cb, x0, y0, x1, y1, ' ', rgb_to_ansi(15, 25, 35))
            # border
            for x in range(x0, x1 + 1):
                self._draw_char(fb, cb, x, y0, width, height, '─', border_color)
                self._draw_char(fb, cb, x, y1, width, height, '─', border_color)
            for y in range(y0, y1 + 1):
                self._draw_char(fb, cb, x0, y, width, height, '│', border_color)
                self._draw_char(fb, cb, x1, y, width, height, '│', border_color)
            # title
            title = " SMARTUP DJ "
            for i, ch in enumerate(title):
                self._draw_char(fb, cb, x0 + 2 + i, y0, width, height, ch, rgb_to_ansi(120, 240, 255))
            # waveform rows
            wave_y = y0 + 1
            bars_row = y0 + height_chars - 2
            for ix in range(width_chars - 2):
                px = x0 + 1 + ix
                # Build multi-harmonic wave
                dx = (ix / (width_chars - 2)) * 6.283 + phase
                amp = 0.5 * math.sin(dx) + 0.3 * math.sin(2.2 * dx + 0.7) + 0.2 * math.sin(3.7 * dx + 1.3)
                amp = (amp * 0.5 + 0.5)
                bar_h = int(amp * max(1, height_chars - 3))
                for iy in range(bar_h):
                    self._draw_char(fb, cb, px, bars_row - iy, width, height, '▌', color_base)
            # progress bar
            prog = (math.sin(phase * 0.5) * 0.5 + 0.5)
            prog_end = int(x0 + 1 + prog * (width_chars - 3))
            for px in range(x0 + 1, prog_end + 1):
                self._draw_char(fb, cb, px, y1, width, height, '█', rgb_to_ansi(120, 220, 255))

        screen_h = 5
        screen_w = max(18, int(platter_r * 1.4))
        draw_deck_screen(cx_left, max(1, cy - platter_r - 6), screen_w, screen_h, self.left_wave_phase, rgb_to_ansi(120, 255, 200))
        draw_deck_screen(cx_right, max(1, cy - platter_r - 6), screen_w, screen_h, self.right_wave_phase, rgb_to_ansi(255, 160, 220))

        # Performance pads (4x2 per deck)
        def draw_pads(origin_x, origin_y):
            cols = 4
            rows = 2
            pad_w = 2
            gap = 2
            for r in range(rows):
                for c in range(cols):
                    px = origin_x + c * (pad_w + gap)
                    py = origin_y + r * 2
                    idx = r * cols + c
                    pulse = (math.sin(self.pad_phase + idx * 0.7) * 0.5 + 0.5)
                    color = rgb_to_ansi(150 + int(105 * pulse), int(80 + 140 * (1 - pulse)), 220)
                    self._draw_char(fb, cb, px, py, width, height, '■', color)
                    self._draw_char(fb, cb, px + 1, py, width, height, '■', color)

        pads_y = min(height - 4, cy + platter_r + 1)
        draw_pads(cx_left - 8, pads_y)
        draw_pads(cx_right - 8, pads_y)

        # Pitch sliders (vertical) near deck sides
        rail_color = rgb_to_ansi(180, 190, 210)
        left_pitch_x = min(width - 2, cx_left + platter_r + 3)
        right_pitch_x = max(1, cx_right - platter_r - 3)
        pitch_top = max(2, cy - platter_r)
        pitch_bot = min(height - 3, cy + platter_r)
        pitch_h = max(6, pitch_bot - pitch_top)
        for y in range(pitch_top, pitch_bot + 1):
            self._draw_char(fb, cb, left_pitch_x, y, width, height, '│', rail_color)
            self._draw_char(fb, cb, right_pitch_x, y, width, height, '│', rail_color)
        left_slider_y = int(pitch_bot - self.left_pitch * pitch_h)
        right_slider_y = int(pitch_bot - self.right_pitch * pitch_h)
        for dx in (-1, 0, 1):
            self._draw_char(fb, cb, left_pitch_x + dx, left_slider_y, width, height, '█', self._accent_color(time_offset * 0.7))
            self._draw_char(fb, cb, right_pitch_x + dx, right_slider_y, width, height, '█', self._accent_color(time_offset * 0.9))

        # Play/Cue buttons
        play_color = rgb_to_ansi(120, 255, 120)
        cue_color = rgb_to_ansi(255, 140, 120)
        for deck_cx in (cx_left, cx_right):
            by = min(height - 5, cy + platter_r + 3)
            self._draw_char(fb, cb, deck_cx - 3, by, width, height, '►', play_color)
            self._draw_char(fb, cb, deck_cx + 3, by, width, height, '■', cue_color)

        # Draw mixer controls (4 channels)
        lane_w = (mixer_x1 - mixer_x0) // 4
        lane_xs = [mixer_x0 + lane_w * i + lane_w // 2 for i in range(self.channel_count)]
        fader_top = mixer_y0 + 4
        fader_bot = mixer_y1 - 6
        fader_height = max(8, fader_bot - fader_top)
        knob_color = self._accent_color(time_offset)

        # Channel faders (vertical) and VU meters next to them
        for i, fx in enumerate(lane_xs):
            # rails
            for y in range(fader_top, fader_bot + 1):
                self._draw_char(fb, cb, fx, y, width, height, '│', rail_color)
            # slider
            slider_y = int(fader_bot - self.faders[i] * fader_height)
            for dx in (-1, 0, 1):
                self._draw_char(fb, cb, fx + dx, slider_y, width, height, '█', knob_color)
            # VU to the left of each fader
            vu_x = fx - lane_w // 3
            level = self._clamp(0.25 + 0.6 * self.faders[i] + 0.15 * math.sin(self.vu_phases[i]))
            lit = int(level * (fader_height))
            for yidx in range(fader_height + 1):
                y = fader_bot - yidx
                if yidx <= lit:
                    self._draw_char(fb, cb, vu_x, y, width, height, '█', self._vu_color(yidx / (fader_height + 0.001)))
                else:
                    self._draw_char(fb, cb, vu_x, y, width, height, '░', rgb_to_ansi(70, 80, 95))

        # Crossfader (horizontal) near bottom
        cross_y = mixer_y1 - 3
        cross_x0 = mixer_x0 + 3
        cross_x1 = mixer_x1 - 4
        for x in range(cross_x0, cross_x1 + 1):
            self._draw_char(fb, cb, x, cross_y, width, height, '─', rail_color)
        slider_x = int(cross_x0 + self.crossfader * (cross_x1 - cross_x0))
        for dy in (-1, 0, 1):
            self._draw_char(fb, cb, slider_x, cross_y + dy, width, height, '█', knob_color)
        # Crossfader curve indicator
        curve_y = cross_y - 2
        for off in range(-6, 7):
            x = int((cross_x0 + cross_x1) / 2) + off
            y = curve_y - int(2.0 * math.sin(off / 6.0 * math.pi))
            self._draw_char(fb, cb, x, y, width, height, '·', rgb_to_ansi(140, 150, 170))

        # Two rows of knobs at mixer top
        knobs_per_row = 4
        for row_idx in range(2):
            knob_y = mixer_y0 + 1 + row_idx * 3
            for i in range(knobs_per_row):
                kx = int(mixer_x0 + (i + 0.5) * (mixer_x1 - mixer_x0) / knobs_per_row)
                # small ring
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if abs(dx) + abs(dy) <= 2 and not (dx == 0 and dy == 0):
                            self._draw_char(fb, cb, kx + dx, knob_y + dy, width, height, '•', rail_color)
                # indicator
                idx = row_idx * knobs_per_row + i
                ang = -math.pi * 0.75 + self.knobs[idx] * (1.5 * math.pi)
                ix = int(kx + math.cos(ang) * 2)
                iy = int(knob_y + math.sin(ang) * 1)
                self._draw_char(fb, cb, ix, iy, width, height, '◆', knob_color)

        # Master VU meters (L/R) near crossfader
        master_left_x = mixer_x0 + 2
        master_right_x = mixer_x1 - 2
        vu_top = mixer_y0 + 6
        vu_bot = cross_y - 5
        vu_h = max(8, vu_bot - vu_top)
        for (mx, phase_off) in [(master_left_x, 0.0), (master_right_x, 1.7)]:
            level = self._clamp(0.5 + 0.45 * math.sin(self.master_vu_phase + phase_off))
            lit = int(level * vu_h)
            for yidx in range(vu_h + 1):
                y = vu_bot - yidx
                if yidx <= lit:
                    self._draw_char(fb, cb, mx, y, width, height, '█', self._vu_color(yidx / (vu_h + 0.001)))
                else:
                    self._draw_char(fb, cb, mx, y, width, height, '░', rgb_to_ansi(70, 80, 95))

        # Center OLED-like label under top knobs
        oled_y0 = mixer_y0 + 7
        oled_y1 = oled_y0 + 2
        oled_x0 = mixer_x0 + 6
        oled_x1 = mixer_x1 - 6
        self._draw_rect(fb, cb, oled_x0, oled_y0, oled_x1, oled_y1, ' ', rgb_to_ansi(10, 15, 22))
        text = " DiesiOslo • SMARTUP "
        tx = oled_x0 + max(0, (oled_x1 - oled_x0 + 1 - len(text)) // 2)
        pulse = (math.sin(self.logo_pulse) * 0.5 + 0.5)
        text_color = rgb_to_ansi(120 + int(80 * pulse), 220, 255)
        for i, ch in enumerate(text):
            self._draw_char(fb, cb, tx + i, oled_y0 + 1, width, height, ch, text_color)

        # LED ambiance along top and sides
        for x in range(0, width, 3):
            c = rgb_to_ansi(60, 120 + int(100 * (math.sin(x * 0.2 + time_offset) * 0.5 + 0.5)), 255)
            self._draw_char(fb, cb, x, 1, width, height, '•', c)
            self._draw_char(fb, cb, x + 1 if x + 1 < width else x, height - 3, width, height, '•', rgb_to_ansi(255, 120, 220))
        

        # Convert buffers to rows
        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                row += cb[y][x] + fb[y][x]
            pattern.append(row + reset_color())

        return pattern


