import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class ForestRaveVisual(VisualBase):
    """Surreal forest pan that reveals a neon mouse rave hidden in a tree hollow."""

    metadata = {
        "name": "Forest Hollow Rave",
        "author": "gadana",
        "version": "1.1",
        "description": "First-person forest pan leading to a neon mouse rave hidden in a tree hollow",
        "ai_creator": "gpt-5-codex",
    }

    def __init__(self):
        self.base_pan_speed = 0.8
        self.slow_strength = 0.6

        self.pan_duration = 6.0
        self.reveal_duration = 4.0
        self.rave_duration = 8.0
        self.exit_duration = 4.0
        self.cycle_duration = (
            self.pan_duration
            + self.reveal_duration
            + self.rave_duration
            + self.exit_duration
        )

        # Focus integral per cycle drives how much the camera slows each loop
        self.focus_integral_per_cycle = (
            0.5 * self.reveal_duration
            + self.rave_duration
            + 0.5 * self.exit_duration
        )

        # Procedural forest layout: few chunky trees with depth + branch direction
        self.side_trees = [
            {"offset": 0.08, "depth": 0.92, "base_width": 1.5, "branch_dir": -1},
            {"offset": 0.28, "depth": 0.74, "base_width": 2.3, "branch_dir": -1},
            {"offset": 0.62, "depth": 0.6, "base_width": 2.2, "branch_dir": 1},
            {"offset": 0.9, "depth": 0.88, "base_width": 1.6, "branch_dir": 1},
        ]

        # Exactly three mice: two dancers + one DJ
        self.mice_layout = [
            {
                "role": "dancer",
                "offset": (-0.35, 0.25),
                "bounce": 1.3,
                "tempo": 2.2,
                "phase": 0.0,
                "frames": [
                    [" /o\\ ", "( ^ )", "/ | \\"],
                    [" \\o/ ", "( x )", "/   \\"],
                ],
            },
            {
                "role": "dancer",
                "offset": (0.35, 0.28),
                "bounce": 1.1,
                "tempo": 2.4,
                "phase": 1.8,
                "frames": [
                    [" \\^/ ", "( o )", "/ # \\"],
                    [" / \\ ", "( ^ )", "/ | \\"],
                ],
            },
            {
                "role": "dj",
                "offset": (0.0, -0.05),
                "bounce": 0.5,
                "tempo": 1.6,
                "phase": 0.9,
                "frames": [
                    [" /@\\ ", "( - )", "/_|_\\"],
                    [" /@\\ ", "( ^ )", "/_|_\\"],
                ],
            },
        ]

        self.dj_table = [
            "|------|",
            "| DJ  |",
            "|______|",
        ]

    def _ease(self, value):
        value = max(0.0, min(1.0, value))
        return 0.5 - 0.5 * math.cos(math.pi * value)

    def _ease_integral(self, value):
        value = max(0.0, min(1.0, value))
        return 0.5 * value - math.sin(math.pi * value) / (2 * math.pi)

    def _exit_integral(self, value):
        value = max(0.0, min(1.0, value))
        return 0.5 * value + math.sin(math.pi * value) / (2 * math.pi)

    def _focus_state(self, phase):
        """Return (focus, partial_integral) for the current phase within the cycle."""
        if phase < self.pan_duration:
            return 0.0, 0.0

        if phase < self.pan_duration + self.reveal_duration:
            reveal_phase = (phase - self.pan_duration) / self.reveal_duration
            focus = self._ease(reveal_phase)
            integral = self.reveal_duration * self._ease_integral(reveal_phase)
            return focus, integral

        if phase < self.pan_duration + self.reveal_duration + self.rave_duration:
            spent = phase - self.pan_duration - self.reveal_duration
            integral = 0.5 * self.reveal_duration + spent
            return 1.0, integral

        u = (phase - self.pan_duration - self.reveal_duration - self.rave_duration) / self.exit_duration
        focus = max(0.0, 1.0 - self._ease(u))
        integral = (
            0.5 * self.reveal_duration
            + self.rave_duration
            + self.exit_duration * self._exit_integral(u)
        )
        return focus, integral

    def _forest_color(self, depth):
        depth = max(0.0, min(1.0, depth))
        r = 10 + int(30 * depth)
        g = 40 + int(100 * depth)
        b = 25 + int(80 * depth)
        return rgb_to_ansi(r, g, b)

    def _party_palette(self, phase, intensity):
        hue = phase + 2.0 * intensity
        r = 150 + 70 * math.sin(hue)
        g = 80 + 120 * math.sin(hue + 2.094)
        b = 150 + 90 * math.sin(hue + 4.188)
        mix = 0.4 + 0.6 * intensity
        r = max(0, min(255, r * mix + 80 * intensity))
        g = max(0, min(255, g * mix + 40 * intensity))
        b = max(0, min(255, b * mix + 120 * intensity))
        return rgb_to_ansi(r, g, b)

    def _build_side_trees(self, width, height, center_x, approach, pan_shift):
        trees = []
        scale_push = 1.0 + approach * 0.75
        for spec in self.side_trees:
            ratio = (spec["offset"] - pan_shift) % 1.0
            x_pos = ratio * width
            dist = x_pos - center_x
            x_pos = center_x + dist * scale_push
            half = spec["base_width"] * (1.3 + (1.0 - spec["depth"]) * (0.8 + 0.6 * approach))
            if x_pos + half < -2 or x_pos - half > width + 2:
                continue
            top = int(height * (0.18 + 0.22 * spec["depth"]))
            trees.append(
                {
                    "x": x_pos,
                    "half": half,
                    "top": top,
                    "depth": spec["depth"],
                    "color": self._forest_color(0.35 + 0.45 * spec["depth"]),
                    "branch_dir": spec["branch_dir"],
                }
            )
        trees.sort(key=lambda tree: tree["depth"], reverse=True)
        return trees

    def _stamp_sprite(self, overlay, sprite_lines, center_x, center_y, color, width, height):
        if not sprite_lines:
            return
        sprite_height = len(sprite_lines)
        sprite_width = max(len(line) for line in sprite_lines)
        top = int(round(center_y - sprite_height / 2))
        left = int(round(center_x - sprite_width / 2))
        for r, line in enumerate(sprite_lines):
            for c, ch in enumerate(line):
                if ch == " ":
                    continue
                px = left + c
                py = top + r
                if 0 <= px < width and 0 <= py < height:
                    overlay[(px, py)] = (ch, color)

    def _build_mice_overlay(self, width, height, center_x, center_y, radius_x, radius_y, t, energy):
        overlay = {}
        for idx, mouse in enumerate(self.mice_layout):
            frames = mouse["frames"]
            tempo = mouse.get("tempo", 1.8)
            oscillation = math.sin(t * tempo + mouse["phase"])
            frame_idx = 0
            if len(frames) > 1 and oscillation < 0:
                frame_idx = 1
            sprite = frames[frame_idx]
            bounce = oscillation * mouse["bounce"]
            anchor_x = center_x + mouse["offset"][0] * radius_x * 1.2
            anchor_y = center_y + mouse["offset"][1] * radius_y + bounce
            color = self._party_palette(t * 1.6 + idx * 0.8, min(1.0, 0.5 + 0.5 * energy))
            self._stamp_sprite(overlay, sprite, anchor_x, anchor_y, color, width, height)

        table_width = len(self.dj_table[0])
        table_height = len(self.dj_table)
        table_x = int(round(center_x - table_width / 2))
        table_y = int(round(center_y + radius_y * 0.25))
        table_color = self._party_palette(t * 0.9, min(1.0, 0.4 + 0.6 * energy))
        for r, line in enumerate(self.dj_table):
            for c, ch in enumerate(line):
                if ch == " ":
                    continue
                px = table_x + c
                py = table_y + r
                if 0 <= px < width and 0 <= py < height:
                    overlay[(px, py)] = (ch, table_color)

        return overlay

    def _render_interior(self, width, height, t, energy, wall_mix, mode):
        center_x = width / 2
        center_y = height / 2 + math.sin(t * 0.8) * (0.3 if mode == "inside" else 0.1)
        radius_x = max(10.0, width * 0.35)
        radius_y = radius_x * 0.65

        overlays = self._build_mice_overlay(width, height, center_x, center_y, radius_x, radius_y, t, energy)

        pattern = []
        for y in range(height):
            row_chars = []
            for x in range(width):
                dx = (x - center_x) / radius_x
                dy = (y - center_y) / radius_y
                dist = math.hypot(dx, dy)
                char = " "
                color = ""

                if dist > 1.18:
                    char = " "
                elif dist > 1.0:
                    rim = min(1.0, (dist - 1.0) / 0.18)
                    wood_blend = min(1.0, rim + wall_mix * 0.5)
                    char = "#"
                    color = self._forest_color(0.7 + 0.3 * wood_blend)
                else:
                    angle = math.atan2(dy, dx + 1e-6)
                    light_wave = 0.5 + 0.5 * math.sin(angle * 4.0 + t * 4.2)
                    radial = 0.5 + 0.5 * math.cos(dist * 6.5 - t * 3.4)
                    intensity = max(0.0, min(1.0, (light_wave * 0.65 + radial * 0.35) * (0.45 + 0.55 * energy)))
                    char = "." if intensity < 0.4 else "*" if intensity < 0.75 else "#"
                    color = self._party_palette(t * 1.3 + angle * 2.5 + dist * 3.0, intensity)

                    floor_line = center_y + radius_y * 0.32
                    if y >= floor_line and dist < 0.95:
                        stripe = int((y - floor_line) // 1) % 2 == 0
                        char = "_" if stripe else "-"
                        floor_intensity = 0.4 + 0.6 * intensity
                        color = rgb_to_ansi(60 + int(90 * floor_intensity), 20 + int(30 * floor_intensity), 95)

                key = (x, y)
                if key in overlays:
                    overlay_char, overlay_color = overlays[key]
                    row_chars.append(overlay_color + overlay_char if overlay_color else overlay_char)
                else:
                    row_chars.append(color + char if color else char)

            pattern.append("".join(row_chars) + reset_color())

        return pattern

    def _render_forest(self, width, height, t, scroll, center_x, center_y, zoom, approach, party_intensity, stage_label):
        pattern = []
        base_radius = max(2.5, min(width, height) * 0.08)
        target_radius = base_radius * (1.0 + 3.6 * approach)
        diag = math.hypot(width, height)
        hollow_radius = min(target_radius, diag * 1.15)
        vertical_scale = 0.65 + 0.2 * zoom
        glow_reach = hollow_radius + 5 + approach * 8.0
        tunnel_ratio = max(0.0, min(1.0, (hollow_radius - diag * 0.6) / (diag * 0.4)))
        ground_y = height - 2
        pan_shift = (scroll * 0.07) % 1.0
        side_trees = self._build_side_trees(width, height, center_x, approach, pan_shift)

        for y in range(height):
            y_ratio = y / max(1, height - 1)
            sky_color = rgb_to_ansi(5, 15 + int(45 * (1 - y_ratio)), 30 + int(30 * (1 - y_ratio)))
            ground_color = self._forest_color(0.85)
            row_chars = []

            for x in range(width):
                char = " "
                color = sky_color

                if y >= ground_y:
                    char = "_"
                    color = ground_color
                else:
                    star_noise = math.sin(0.15 * x + 0.21 * y + t * 0.8)
                    if star_noise > 0.996:
                        char = "."
                        color = sky_color

                # Side trunks (chunky, spaced)
                for tree in side_trees:
                    if y < tree["top"] or y >= ground_y:
                        continue
                    dx_tree = x - tree["x"]
                    if abs(dx_tree) <= tree["half"]:
                        edge = tree["half"] - abs(dx_tree)
                        trunk_char = "#"
                        if y <= tree["top"] + 1 and edge < 0.8:
                            trunk_char = "/" if tree["branch_dir"] < 0 else "\\"
                        elif edge < 0.4:
                            trunk_char = "|"
                        char = trunk_char
                        color = tree["color"]
                        break

                # Main tree trunk
                dx_main = x - center_x
                trunk_top = int(max(0, center_y - height * (0.32 + 0.08 * (1.0 - min(1.0, approach + 0.1)))))
                main_half = min(width / 2, 2.2 + zoom * 2.8)
                if trunk_top <= y <= ground_y and abs(dx_main) <= main_half:
                    bark_toggle = (int(y * 0.25) + int(abs(dx_main))) % 2
                    char = "#" if bark_toggle else "|"
                    color = self._forest_color(1.0)
                    if y <= trunk_top + 1 and abs(abs(dx_main) - main_half) < 0.8:
                        char = "/" if dx_main < 0 else "\\"

                # Hollow interior and glow
                dy = (y - center_y) / max(0.001, vertical_scale)
                distance = math.hypot(dx_main, dy)
                rim_band = 0.9 + approach * 0.7
                inside_threshold = hollow_radius * (1.0 - 0.02 * (1.0 - approach))
                inside_hollow = distance <= inside_threshold
                rim_zone = abs(distance - hollow_radius) <= rim_band

                if inside_hollow:
                    fill_intensity = max(0.15, party_intensity)
                    char = "-" if party_intensity < 0.2 else ("*" if math.sin(distance * 0.1 + t * 2.3) > 0 else "=")
                    color = self._party_palette(t * 2.0 + distance * 0.18, fill_intensity)
                elif rim_zone:
                    char = ")" if dx_main > 0 else "("
                    color = self._forest_color(0.9)
                elif tunnel_ratio > 0.65 and distance <= hollow_radius * 1.1 and y < ground_y:
                    char = "|"
                    color = self._forest_color(0.95)

                if not inside_hollow and distance <= glow_reach and party_intensity > 0.05:
                    beam = max(0.0, 1.0 - max(0.0, distance - hollow_radius) / max(1.0, glow_reach - hollow_radius))
                    angle = math.atan2(dy, dx_main + 1e-6)
                    beam *= (0.5 + 0.5 * math.sin(angle * 4 + t * 5.0))
                    beam *= party_intensity
                    if beam > 0.3:
                        char = "*" if beam > 0.65 else "."
                        color = self._party_palette(t * 1.2 + distance * 0.05, min(1.0, beam + 0.3))

                row_chars.append(color + char if color else char)

            pattern.append("".join(row_chars) + reset_color())

        return pattern

    def generate_frame(self, width, height, time_offset):
        if width < 30 or height < 12:
            return ["Terminal too small".ljust(width) for _ in range(height)]

        t = time_offset
        cycle_index = math.floor(t / self.cycle_duration)
        phase = t - cycle_index * self.cycle_duration
        focus, focus_integral_partial = self._focus_state(phase)
        focus_integral_total = cycle_index * self.focus_integral_per_cycle + focus_integral_partial

        scroll = self.base_pan_speed * (t - self.slow_strength * focus_integral_total)
        wobble = math.sin(t * 1.2) * (0.5 + 0.4 * (1.0 - focus))
        party_intensity = max(0.0, min(1.0, 0.2 + 0.8 * focus))

        pan_end = self.pan_duration
        enter_end = pan_end + self.reveal_duration
        inside_end = enter_end + self.rave_duration

        forest_stage = None
        forest_approach = 0.0
        interior_energy = 0.0
        wall_mix = 0.0
        interior_mode = None

        if phase < pan_end:
            forest_stage = "pan"
            forest_approach = 0.0
        elif phase < enter_end:
            forest_stage = "enter"
            forest_approach = (phase - pan_end) / self.reveal_duration
        elif phase < inside_end:
            interior_mode = "inside"
            interior_energy = 1.0
            wall_mix = min(0.4, (phase - enter_end) / max(1.0, self.rave_duration) * 0.4)
        else:
            exit_phase = (phase - inside_end) / self.exit_duration
            exit_phase = max(0.0, min(1.0, exit_phase))
            if exit_phase < 0.5:
                interior_mode = "exit"
                interior_energy = max(0.2, 1.0 - exit_phase * 1.2)
                wall_mix = min(1.0, exit_phase * 2.0)
            else:
                forest_stage = "exit"
                pull_phase = min(1.0, (exit_phase - 0.5) / 0.5)
                forest_approach = max(0.0, 1.0 - pull_phase)

        if forest_stage:
            center_x = width * (0.68 - 0.25 * forest_approach)
            center_y = height * (0.58 - 0.15 * forest_approach) + wobble * (0.6 + 0.2 * (1.0 - forest_approach))
            zoom = 0.85 + 1.2 * forest_approach
            forest_pattern = self._render_forest(
                width,
                height,
                t,
                scroll,
                center_x,
                center_y,
                zoom,
                forest_approach,
                party_intensity,
                forest_stage,
            )
            return forest_pattern

        interior_pattern = self._render_interior(width, height, t, interior_energy, wall_mix, interior_mode or "inside")
        return interior_pattern
