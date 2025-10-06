import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class DjSet2Visual(VisualBase):
    """Detailed top-down DJ mixer with animated channel strips and FX."""

    metadata = {
        "name": "DJ Set 2",
        "author": "sat",
        "version": "1.0",
        "description": "Top-down pro mixer with animated channels, meters, and crossfader"
    }

    def __init__(self):
        self.channel_count = 4
        self.channel_offsets = [random.uniform(0, math.tau) for _ in range(self.channel_count)]
        self.knob_offsets = [
            [random.uniform(0, math.tau) for _ in range(4)] for _ in range(self.channel_count)
        ]
        self.vu_offsets = [random.uniform(0, math.tau) for _ in range(self.channel_count)]
        self.fader_offsets = [random.uniform(0, math.tau) for _ in range(self.channel_count)]
        self.wave_offsets = [random.uniform(0, math.tau) for _ in range(self.channel_count)]

    def generate_frame(self, width, height, time_offset):
        if width < 44 or height < 18:
            return self._compact_frame(width, height, time_offset)

        grid_chars = [[" "] * width for _ in range(height)]
        grid_colors = [[""] * width for _ in range(height)]

        panel_margin_x = max(1, min(4, width // 20))
        panel_margin_y = max(1, min(3, height // 18))
        left = panel_margin_x
        right = width - panel_margin_x - 1
        top = panel_margin_y
        bottom = height - panel_margin_y - 1

        if left >= right or top >= bottom:
            return self._compact_frame(width, height, time_offset)

        panel_width = right - left + 1
        panel_height = bottom - top + 1

        gap = max(1, panel_width // 32)
        channel_width = (panel_width - gap * (self.channel_count - 1)) // self.channel_count
        if channel_width < 7:
            channel_width = 7
        occupied_width = channel_width * self.channel_count + gap * (self.channel_count - 1)
        start_x = left + max(0, (panel_width - occupied_width) // 2)

        channel_positions = []
        cursor = start_x
        for _ in range(self.channel_count):
            ch_left = cursor
            ch_right = ch_left + channel_width - 1
            channel_positions.append((ch_left, ch_right))
            cursor = ch_right + gap

        frame_color = rgb_to_ansi(90, 95, 120)
        panel_color = rgb_to_ansi(24, 26, 40)
        divider_color = rgb_to_ansi(55, 60, 80)
        label_color = rgb_to_ansi(200, 210, 240)
        text_soft = rgb_to_ansi(140, 150, 190)
        knob_color = rgb_to_ansi(150, 160, 195)
        knob_ring_color = rgb_to_ansi(80, 90, 120)
        fader_track_color = rgb_to_ansi(70, 80, 110)
        fader_cap_color = rgb_to_ansi(255, 150, 80)
        cue_color = rgb_to_ansi(90, 160, 255)
        cross_track_color = rgb_to_ansi(80, 90, 130)
        cross_cap_color = rgb_to_ansi(255, 120, 180)

        channel_wave_colors = [
            rgb_to_ansi(90, 180, 255),
            rgb_to_ansi(120, 255, 210),
            rgb_to_ansi(255, 190, 110),
            rgb_to_ansi(200, 135, 255),
        ]

        vu_low = rgb_to_ansi(70, 220, 120)
        vu_mid = rgb_to_ansi(220, 200, 90)
        vu_high = rgb_to_ansi(255, 90, 80)

        def set_cell(x, y, char, color=""):
            if 0 <= x < width and 0 <= y < height:
                grid_chars[y][x] = char
                grid_colors[y][x] = color

        def draw_horizontal(x0, x1, y, char, color=""):
            if y < 0 or y >= height:
                return
            xa = max(0, min(x0, x1))
            xb = min(width - 1, max(x0, x1))
            for x in range(xa, xb + 1):
                set_cell(x, y, char, color)

        def draw_vertical(x, y0, y1, char, color=""):
            if x < 0 or x >= width:
                return
            ya = max(0, min(y0, y1))
            yb = min(height - 1, max(y0, y1))
            for y in range(ya, yb + 1):
                set_cell(x, y, char, color)

        def draw_border():
            draw_horizontal(left, right, top, "-", frame_color)
            draw_horizontal(left, right, bottom, "-", frame_color)
            draw_vertical(left, top, bottom, "|", frame_color)
            draw_vertical(right, top, bottom, "|", frame_color)
            set_cell(left, top, "+", frame_color)
            set_cell(right, top, "+", frame_color)
            set_cell(left, bottom, "+", frame_color)
            set_cell(right, bottom, "+", frame_color)

        def fill_panel():
            for y in range(top + 1, bottom):
                for x in range(left + 1, right):
                    grid_chars[y][x] = " "
                    grid_colors[y][x] = panel_color

        draw_border()
        fill_panel()

        for idx, (ch_left, ch_right) in enumerate(channel_positions[:-1]):
            divider_x = ch_right + gap // 2
            if divider_x < right:
                draw_vertical(divider_x, top + 1, bottom - 1, ":", divider_color)

        label_y = top + 1
        waveform_y = label_y + 1
        led_y = waveform_y + 1
        fader_bottom = bottom - 2
        max_fader_length = fader_bottom - (led_y + 5)
        fader_length = max(6, min(max_fader_length, int(panel_height * 0.45)))
        if fader_length > max_fader_length:
            fader_length = max_fader_length
        if fader_length < 5:
            fader_length = max(5, fader_bottom - (led_y + 3))
        fader_top = fader_bottom - fader_length + 1
        knob_area_top = led_y + 2
        knob_rows = 4

        for channel_idx, (ch_left, ch_right) in enumerate(channel_positions):
            ch_center = ch_left + (ch_right - ch_left) // 2
            color_wave = channel_wave_colors[channel_idx % len(channel_wave_colors)]
            label = f"CH{channel_idx + 1}"
            label_start = ch_center - len(label) // 2
            for pos, char in enumerate(label):
                set_cell(label_start + pos, label_y, char, label_color)

            wave_phase = time_offset * 1.8 + self.wave_offsets[channel_idx]
            for x in range(ch_left + 1, ch_right):
                local = (x - (ch_left + 1)) / max(1, (ch_right - ch_left - 1))
                wave = math.sin(local * math.pi * 3 + wave_phase)
                wave += 0.3 * math.sin(local * math.pi * 5 - wave_phase * 0.6)
                if wave > 0.6:
                    char = "^"
                elif wave > 0.2:
                    char = "/"
                elif wave > -0.2:
                    char = "-"
                elif wave > -0.6:
                    char = "\\"
                else:
                    char = "_"
                set_cell(x, waveform_y, char, color_wave)

            led_count = min(5, max(3, channel_width // 2))
            led_spacing = (ch_right - ch_left - 2) / (led_count + 1)
            for led_idx in range(led_count):
                led_x = int(ch_left + 1 + (led_idx + 1) * led_spacing)
                led_phase = time_offset * 4 + self.channel_offsets[channel_idx] + led_idx * 0.9
                led_strength = (math.sin(led_phase) + 1) / 2
                led_char = "O" if led_strength > 0.65 else "o"
                led_intensity = int(120 + 120 * led_strength)
                led_color = rgb_to_ansi(led_intensity, 80, 150)
                set_cell(led_x, led_y, led_char, led_color)

            available_for_knobs = max(0, fader_top - 5 - knob_area_top)
            knob_positions = []
            if knob_rows == 1 or available_for_knobs <= 0:
                knob_positions = [knob_area_top]
            else:
                for knob_idx in range(knob_rows):
                    t = knob_idx / max(1, knob_rows - 1)
                    pos_y = knob_area_top + int(round(t * available_for_knobs))
                    knob_positions.append(pos_y)
            knob_labels = ["TRM", "HI", "MID", "LOW"]
            for knob_idx, knob_y in enumerate(knob_positions):
                if knob_y >= fader_top - 4:
                    break
                label_text = knob_labels[min(knob_idx, len(knob_labels) - 1)]
                label_x = ch_left + 1
                for pos, char in enumerate(label_text):
                    if label_x + pos < ch_right:
                        set_cell(label_x + pos, knob_y, char, text_soft)

                knob_center = ch_center
                knob_left = knob_center - 2
                knob_right = knob_center + 2
                set_cell(knob_left, knob_y, "(", knob_ring_color)
                set_cell(knob_right, knob_y, ")", knob_ring_color)
                set_cell(knob_center - 1, knob_y, " ", panel_color)
                set_cell(knob_center + 1, knob_y, " ", panel_color)
                set_cell(knob_center, knob_y, "@", knob_color)

                sweep_phase = time_offset * 0.7 + self.knob_offsets[channel_idx][knob_idx % 4]
                direction = math.sin(sweep_phase)
                pointer_offset = int(round(direction * 2))
                pointer_x = max(knob_left + 1, min(knob_right - 1, knob_center + pointer_offset))
                pointer_char = "^" if pointer_offset == 0 else ("/" if pointer_offset > 0 else "\\")
                set_cell(pointer_x, knob_y - 1, pointer_char, knob_color)

            vu_top = min(fader_top - 3, knob_positions[-1] + 2 if knob_positions else knob_area_top)
            vu_bottom = fader_top - 3
            if vu_bottom <= vu_top:
                vu_top = max(knob_area_top, vu_bottom - 3)
            vu_height = max(3, vu_bottom - vu_top + 1)
            vu_width = max(2, channel_width // 4)
            vu_left = ch_left + 1
            vu_right = vu_left + vu_width - 1
            level_phase = time_offset * 3 + self.vu_offsets[channel_idx]
            level = (math.sin(level_phase) + math.sin(level_phase * 0.37 + 1.2)) / 2
            level = (level + 1) / 2
            active_height = int(round(level * (vu_height - 1)))
            for ix in range(vu_left, vu_right + 1):
                for offset in range(vu_height):
                    y = vu_bottom - offset
                    if y < vu_top:
                        continue
                    ratio = offset / max(1, vu_height - 1)
                    if offset <= active_height:
                        if ratio < 0.55:
                            color = vu_low
                        elif ratio < 0.8:
                            color = vu_mid
                        else:
                            color = vu_high
                        char = "#"
                    else:
                        color = divider_color
                        char = "."
                    set_cell(ix, y, char, color)

            fader_x = ch_center
            draw_vertical(fader_x, fader_top, fader_bottom, "|", fader_track_color)
            fader_phase = time_offset * 0.6 + self.fader_offsets[channel_idx]
            fader_value = (math.sin(fader_phase) + 1) / 2
            slider_y = int(round(fader_bottom - fader_value * (fader_length - 1)))
            slider_y = max(fader_top, min(fader_bottom, slider_y))
            for dx in (-1, 0, 1):
                if ch_left < fader_x + dx < ch_right:
                    set_cell(fader_x + dx, slider_y, "#", fader_cap_color)

            cue_y = min(fader_bottom + 1, bottom - 1)
            cue_label = "CUE"
            cue_start = ch_center - len(cue_label) // 2
            blink = math.sin(time_offset * 2 + self.channel_offsets[channel_idx])
            cue_active = blink > 0.3 if channel_idx % 2 == 0 else blink < -0.3
            cue_col = cue_color if cue_active else divider_color
            for pos, char in enumerate(cue_label):
                set_cell(cue_start + pos, cue_y, char, cue_col)

        cross_y = bottom - 1
        cross_left = channel_positions[0][0] + 1
        cross_right = channel_positions[-1][1] - 1
        draw_horizontal(cross_left, cross_right, cross_y, "=", cross_track_color)
        cross_phase = time_offset * 0.5
        cross_value = (math.sin(cross_phase) + 1) / 2
        cross_x = int(round(cross_left + cross_value * (cross_right - cross_left)))
        for dx in (-1, 0, 1):
            set_cell(cross_x + dx, cross_y, "#", cross_cap_color)
        set_cell(max(left + 2, cross_left), cross_y - 1, "A", label_color)
        set_cell(min(right - 2, cross_right), cross_y - 1, "B", label_color)

        master_label = "MASTER"
        draw_horizontal(cross_left, cross_right, cross_y - 2, "-", divider_color)
        master_start = left + (panel_width - len(master_label)) // 2
        for pos, char in enumerate(master_label):
            set_cell(master_start + pos, cross_y - 3, char, label_color)

        pattern = []
        for y in range(height):
            row = ""
            for x in range(width):
                color = grid_colors[y][x]
                char = grid_chars[y][x]
                row += (color + char) if color else char
            pattern.append(row + reset_color())

        return pattern

    def _compact_frame(self, width, height, time_offset):
        message = "DJ MIXER"
        sub = "need more space"
        pattern = []
        center_y = height // 2
        for y in range(height):
            if y == center_y:
                start = max(0, (width - len(message)) // 2)
                row = " " * start + message + " " * max(0, width - start - len(message))
            elif y == center_y + 1 and height > center_y + 1:
                start = max(0, (width - len(sub)) // 2)
                row = " " * start + sub + " " * max(0, width - start - len(sub))
            else:
                row = " " * width
            pattern.append(row + reset_color())
        return pattern
