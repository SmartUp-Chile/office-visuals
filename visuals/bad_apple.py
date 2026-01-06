import os
import sys
import threading
import urllib.request
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.visual_base import VisualBase
from core.utils import rgb_to_ansi, reset_color


class BadAppleVisual(VisualBase):
    """ASCII rendition of Bad Apple using cached frames."""

    metadata = {
        "name": "Bad Apple ASCII",
        "author": "gadana",
        "version": "1.0",
        "description": "Legendary Bad Apple silhouette animation rendered with cached ASCII frames",
        "ai_creator": None,
    }

    DATA_URL = "https://raw.githubusercontent.com/skanehira/badapple.vim/master/resources/badapple.txt"
    DENSITY_RAMP = " .'`^\",:;Ili~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

    def __init__(self):
        asset_dir = os.path.join(os.path.dirname(__file__), "assets", "badapple")
        os.makedirs(asset_dir, exist_ok=True)
        self.data_path = os.path.join(asset_dir, "badapple.txt")
        self.frames: List[List[bytearray]] | None = None
        self.source_width = 100
        self.source_height = 30
        self.playback_fps = 16.0
        self.status_message = "Preparando Bad Apple..."
        self.load_error: str | None = None
        self._download_thread: threading.Thread | None = None
        self._intensity_cache: dict[str, float] = {}
        self.contrast_power = 1.06
        self.char_threshold = 0.028

    def generate_frame(self, width, height, time_offset):
        self._ensure_frames()

        if self.load_error:
            message = [
                "❌ No pude preparar Bad Apple",
                self.load_error,
                "Coloca badapple.txt en visuals/assets/badapple/ para usar tu copia.",
            ]
            return self._render_message(width, height, message)

        if self.frames is None:
            message = [
                self.status_message or "Descargando Bad Apple...",
                "Fuente: skanehira/badapple.vim (MIT)",
            ]
            return self._render_message(width, height, message)

        if width < 24 or height < 12:
            return self._render_message(
                width, height, ["Amplía la terminal", "para disfrutar Bad Apple"]
            )

        frame_index = int(time_offset * self.playback_fps)
        frame_index %= len(self.frames)
        frame_data = self.frames[frame_index]
        return self._render_frame(frame_data, width, height)

    def _ensure_frames(self):
        if self.frames or self.load_error:
            return

        if os.path.exists(self.data_path):
            try:
                self.frames = self._load_frames_from_file(self.data_path)
                self.status_message = None
            except Exception as exc:
                self.load_error = f"Archivo corrupto: {exc}"
            return

        if self._download_thread is None:
            self.status_message = "Descargando Bad Apple ASCII (~6 MB)..."
            self._download_thread = threading.Thread(
                target=self._download_dataset, daemon=True
            )
            self._download_thread.start()

    def _download_dataset(self):
        tmp_path = self.data_path + ".tmp"
        try:
            with urllib.request.urlopen(self.DATA_URL) as response, open(
                tmp_path, "wb"
            ) as output:
                total = int(response.headers.get("Content-Length", "0") or "0")
                downloaded = 0
                while True:
                    chunk = response.read(65536)
                    if not chunk:
                        break
                    output.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        pct = int(downloaded / total * 100)
                        self.status_message = (
                            f"Descargando Bad Apple ASCII ({pct}%)..."
                        )
                    else:
                        kb = downloaded // 1024
                        self.status_message = (
                            f"Descargando Bad Apple ASCII ({kb} KB)..."
                        )
            os.replace(tmp_path, self.data_path)
            self.status_message = "Descarga completa, cargando frames..."
        except Exception as exc:
            self.load_error = f"Descarga falló: {exc}"
            self.status_message = self.load_error
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        finally:
            self._download_thread = None

    def _load_frames_from_file(self, path):
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            data = handle.read()

        chunks = data.split("SPLIT")
        raw_frames = []
        max_height = 0
        max_width = 0
        for chunk in chunks:
            stripped = chunk.strip("\n")
            if not stripped:
                continue
            lines = stripped.splitlines()
            if not lines:
                continue
            raw_frames.append(lines)
            max_height = max(max_height, len(lines))
            max_width = max(
                max_width,
                max((len(line) for line in lines), default=0),
            )

        if not raw_frames:
            raise ValueError("no encontré frames en el archivo")

        self.source_height = max_height
        self.source_width = max_width
        processed_frames: List[List[bytearray]] = []
        for lines in raw_frames:
            matrix = []
            for y in range(self.source_height):
                line = lines[y] if y < len(lines) else ""
                row = bytearray(self.source_width)
                limit = min(len(line), self.source_width)
                for x in range(limit):
                    row[x] = int(self._char_intensity(line[x]) * 255)
                matrix.append(row)
            processed_frames.append(matrix)
        return processed_frames

    def _render_frame(self, frame_data, width, height):
        if self.source_width == 0 or self.source_height == 0:
            return self._render_message(width, height, ["Sin datos de Bad Apple"])

        scale_x = width / self.source_width
        scale_y = height / self.source_height
        scale = max(0.1, min(scale_x, scale_y))
        target_w = max(1, min(width, int(self.source_width * scale)))
        target_h = max(1, min(height, int(self.source_height * scale)))
        pad_left = max(0, (width - target_w) // 2)
        pad_right = max(0, width - pad_left - target_w)
        pad_top = max(0, (height - target_h) // 2)
        pad_bottom = max(0, height - pad_top - target_h)

        scale_x = (self.source_width - 1) / max(1, target_w - 1)
        scale_y = (self.source_height - 1) / max(1, target_h - 1)

        inv_255 = 1.0 / 255.0
        pattern = []
        blank_line = " " * width
        for _ in range(pad_top):
            pattern.append(blank_line + reset_color())

        for ty in range(target_h):
            src_y = ty * scale_y
            y0 = int(src_y)
            y1 = min(self.source_height - 1, y0 + 1)
            wy = src_y - y0
            top_row = frame_data[y0]
            bottom_row = frame_data[y1]
            row_chars = []
            for tx in range(target_w):
                src_x = tx * scale_x
                x0 = int(src_x)
                x1 = min(self.source_width - 1, x0 + 1)
                wx = src_x - x0
                i00 = top_row[x0]
                i10 = top_row[x1]
                i01 = bottom_row[x0]
                i11 = bottom_row[x1]
                top = i00 * (1 - wx) + i10 * wx
                bottom = i01 * (1 - wx) + i11 * wx
                intensity = (top * (1 - wy) + bottom * wy) * inv_255
                row_chars.append(self._shade_from_intensity(intensity))

            row = " " * pad_left + "".join(row_chars) + reset_color()
            if pad_right:
                row += " " * pad_right
            pattern.append(row)

        for _ in range(pad_bottom):
            pattern.append(blank_line + reset_color())

        return pattern

    def _shade_from_intensity(self, intensity):
        value = max(0.0, min(1.0, intensity))
        adjusted = value ** self.contrast_power
        if adjusted <= self.char_threshold:
            return reset_color() + " "
        ramp_index = min(len(self.DENSITY_RAMP) - 1, int(adjusted * (len(self.DENSITY_RAMP) - 1)))
        char = self.DENSITY_RAMP[ramp_index]
        level = int(20 + 235 * adjusted)
        color = rgb_to_ansi(level, level, level)
        return color + char

    def _char_intensity(self, char):
        cached = self._intensity_cache.get(char)
        if cached is not None:
            return cached
        idx = self.DENSITY_RAMP.find(char)
        if idx == -1:
            idx = self.DENSITY_RAMP.find(char.lower())
        if idx == -1:
            val = min(1.0, max(0.0, (ord(char) - 32) / 94))
        else:
            val = idx / (len(self.DENSITY_RAMP) - 1)
        self._intensity_cache[char] = val
        return val

    def _render_message(self, width, height, lines):
        if width <= 0 or height <= 0:
            return [""]
        trimmed = [line[:width] for line in lines if line]
        total_lines = len(trimmed)
        top_padding = max(0, (height - total_lines) // 2)
        pattern = []
        blank = " " * width
        for _ in range(top_padding):
            pattern.append(blank + reset_color())

        for line in trimmed:
            visible = line.strip("\n")
            start = max(0, (width - len(visible)) // 2)
            row = " " * start + visible
            row += " " * max(0, width - start - len(visible))
            pattern.append(row + reset_color())

        while len(pattern) < height:
            pattern.append(blank + reset_color())

        return pattern
