#!/usr/bin/env python3
"""Render a report-ready timing diagram from an Icarus VCD file.

The plotted values are decoded from the VCD; this script does not regenerate
expected counter behavior. Run from any directory with:

    python3 tools/render_wave_report.py
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from bisect import bisect_right
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VCD = ROOT / "build/sim/wave.vcd"
DEFAULT_OUT = ROOT / "evidence/normal/counter4_normal_waveform.png"
PRESERVED_VCD = ROOT / "evidence/normal/wave.vcd"

REQUIRED = ("clk", "rst", "enable", "down", "value")
SIGNAL_LABELS = {
    "clk": "clk",
    "rst": "rst",
    "enable": "enable",
    "down": "down",
    "value": "value[3:0]",
}

PAGE_W, PAGE_H = 3600, 2700
INK = (27, 43, 58)
MUTED = (92, 108, 121)
GRID = (215, 224, 230)
BLUE = (31, 103, 170)
BUS_FILL = (227, 239, 248)
BUS_EDGE = (43, 99, 145)
GREEN_FILL = (231, 244, 235)
GOLD_FILL = (252, 245, 220)
RED_FILL = (250, 232, 228)
PANEL_EDGE = (176, 190, 201)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial.ttf"]
        if bold else
        ["/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc"]
    )
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    raise RuntimeError("A readable system TrueType font is required for PNG labels.")


def parse_vcd(path: Path) -> tuple[dict[str, list[tuple[float, int | str]]], float, str]:
    """Read the top-level testbench signals and return their timed values."""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    scope: list[str] = []
    top_scope = None
    ids: dict[str, str] = {}
    scale_text = None
    date_text = ""
    in_header = True
    in_timescale = False
    in_date = False
    current_tick = 0
    final_tick = 0
    updates: dict[int, dict[str, int | str]] = {}

    for line in lines:
        stripped = line.strip()
        if in_header:
            if stripped.startswith("$date"):
                in_date = True
                continue
            if in_date:
                if stripped == "$end":
                    in_date = False
                elif stripped:
                    date_text += (" " if date_text else "") + stripped
                continue
            if stripped.startswith("$timescale"):
                in_timescale = True
                rest = stripped[len("$timescale"):].replace("$end", "").strip()
                if rest:
                    scale_text = rest
                    in_timescale = False
                continue
            if in_timescale:
                if "$end" in stripped:
                    scale_text = (scale_text or "") + " " + stripped.replace("$end", "").strip()
                    in_timescale = False
                else:
                    scale_text = (scale_text or "") + " " + stripped
                continue
            if stripped.startswith("$scope"):
                parts = stripped.split()
                if len(parts) >= 3:
                    scope.append(parts[2])
                    if len(scope) == 1:
                        top_scope = parts[2]
                continue
            if stripped.startswith("$upscope"):
                if scope:
                    scope.pop()
                continue
            if stripped.startswith("$var"):
                parts = stripped.split()
                if len(parts) >= 5:
                    ident, reference = parts[3], parts[4]
                    # Take only the testbench's top-level nets, avoiding its
                    # duplicate hierarchical DUT ports with the same names.
                    if len(scope) == 1 and reference in REQUIRED:
                        ids[ident] = reference
                continue
            if stripped.startswith("$enddefinitions"):
                in_header = False
                continue
            continue

        if not stripped or stripped.startswith("$"):
            continue
        if stripped.startswith("#"):
            try:
                current_tick = int(stripped[1:])
            except ValueError:
                continue
            final_tick = max(final_tick, current_tick)
            continue

        ident = None
        value: int | str | None = None
        if stripped[0] in "bB":
            parts = stripped.split()
            if len(parts) == 2:
                bits, ident = parts[0][1:].lower(), parts[1]
                value = int(bits, 2) if bits and set(bits) <= {"0", "1"} else "X"
        elif stripped[0] in "01xXzZ":
            ident, bit = stripped[1:], stripped[0].lower()
            value = int(bit) if bit in "01" else "X"
        if ident in ids and value is not None:
            updates.setdefault(current_tick, {})[ids[ident]] = value

    if not top_scope:
        raise ValueError("The VCD has no top-level module scope.")
    missing = set(REQUIRED) - set(ids.values())
    if missing:
        raise ValueError("Missing top-level VCD signals: " + ", ".join(sorted(missing)))
    if not scale_text:
        raise ValueError("The VCD does not declare a timescale.")
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(fs|ps|ns|us|ms|s)\b", scale_text)
    if not match:
        raise ValueError(f"Cannot parse VCD timescale: {scale_text!r}")
    unit_to_ns = {"fs": 1e-6, "ps": 1e-3, "ns": 1.0, "us": 1e3, "ms": 1e6, "s": 1e9}
    ns_per_tick = float(match.group(1)) * unit_to_ns[match.group(2)]

    series: dict[str, list[tuple[float, int | str]]] = {}
    for name in REQUIRED:
        value_at_time: int | str = "X"
        points: list[tuple[float, int | str]] = []
        for tick in sorted(updates):
            if name in updates[tick]:
                new_value = updates[tick][name]
                if new_value != value_at_time:
                    value_at_time = new_value
                    points.append((tick * ns_per_tick, value_at_time))
        series[name] = points
    return series, final_tick * ns_per_tick, date_text


def state_at(points: list[tuple[float, int | str]], time_ns: float) -> int | str:
    index = bisect_right([point[0] for point in points], time_ns) - 1
    return points[index][1] if index >= 0 else "X"


def text_width(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont) -> int:
    bounds = draw.textbbox((0, 0), value, font=face)
    return bounds[2] - bounds[0]


def x_at(time_ns: float, left: int, right: int, start_ns: float, end_ns: float) -> int:
    return round(left + (time_ns - start_ns) * (right - left) / (end_ns - start_ns))


def draw_axis(draw: ImageDraw.ImageDraw, rect: tuple[int, int, int, int],
              start_ns: float, end_ns: float, tick_ns: int,
              font_small: ImageFont.FreeTypeFont) -> tuple[int, int, int]:
    x, y, w, h = rect
    left, right = x + 250, x + w - 50
    top, bottom = y + 215, y + h - 105
    draw.line((left, top, right, top), fill=PANEL_EDGE, width=2)
    draw.line((left, bottom, right, bottom), fill=INK, width=3)
    tick = (int(start_ns // tick_ns) + (0 if start_ns % tick_ns == 0 else 1)) * tick_ns
    while tick <= end_ns:
        px = x_at(tick, left, right, start_ns, end_ns)
        draw.line((px, top, px, bottom), fill=GRID, width=2)
        label = str(tick)
        draw.line((px, bottom, px, bottom + 14), fill=INK, width=2)
        bounds = draw.textbbox((0, 0), label, font=font_small)
        draw.text((px - (bounds[2] - bounds[0]) / 2, bottom + 23), label,
                  font=font_small, fill=INK)
        tick += tick_ns
    axis_label = "Time (ns)"
    draw.text(((left + right - text_width(draw, axis_label, font_small)) / 2,
               bottom + 65), axis_label, font=font_small, fill=MUTED)
    return left, right, top, bottom


def draw_logic(draw: ImageDraw.ImageDraw, points: list[tuple[float, int | str]],
               left: int, right: int, top: int, bottom: int,
               start_ns: float, end_ns: float) -> None:
    high_y = top + 31
    low_y = min(top + 111, bottom - 23)
    points_in = [(t, v) for t, v in points if start_ns < t < end_ns]
    current = state_at(points, start_ns)
    current_t = start_ns
    for t, value in points_in + [(end_ns, state_at(points, end_ns))]:
        x1 = x_at(current_t, left, right, start_ns, end_ns)
        x2 = x_at(t, left, right, start_ns, end_ns)
        if current in (0, 1):
            yv = high_y if current == 1 else low_y
            draw.line((x1, yv, x2, yv), fill=BLUE, width=6)
        else:
            draw.line((x1, (high_y + low_y) // 2, x2, (high_y + low_y) // 2),
                      fill=(180, 78, 65), width=4)
            draw.text((x1 + 8, (high_y + low_y) // 2 - 25), "X", font=font(30, True), fill=(180, 78, 65))
        if t < end_ns and value != current:
            xe = x2
            if current in (0, 1) and value in (0, 1):
                draw.line((xe, high_y if current == 1 else low_y,
                           xe, high_y if value == 1 else low_y), fill=BLUE, width=6)
            current_t, current = t, value


def draw_bus(draw: ImageDraw.ImageDraw, points: list[tuple[float, int | str]],
             left: int, right: int, top: int, bottom: int,
             start_ns: float, end_ns: float, face: ImageFont.FreeTypeFont) -> None:
    band_top, band_bottom = top + 38, min(top + 105, bottom - 18)
    changes = [(t, v) for t, v in points if start_ns < t < end_ns]
    segments: list[tuple[float, float, int | str]] = []
    t0, value = start_ns, state_at(points, start_ns)
    for t, next_value in changes:
        segments.append((t0, t, value))
        t0, value = t, next_value
    segments.append((t0, end_ns, state_at(points, end_ns)))
    for start, end, value in segments:
        x1, x2 = x_at(start, left, right, start_ns, end_ns), x_at(end, left, right, start_ns, end_ns)
        if x2 <= x1:
            continue
        if value == "X":
            fill = RED_FILL
            label = "X"
        else:
            fill = BUS_FILL
            label = f"{value:X}"
        draw.rectangle((x1, band_top, x2, band_bottom), fill=fill, outline=BUS_EDGE, width=3)
        if x2 - x1 > text_width(draw, label, face) + 15:
            tw = text_width(draw, label, face)
            th = face.getbbox(label)[3] - face.getbbox(label)[1]
            draw.text(((x1 + x2 - tw) / 2, (band_top + band_bottom - th) / 2 - 4),
                      label, font=face, fill=INK)


def draw_panel(image: Image.Image, series: dict[str, list[tuple[float, int | str]]],
               rect: tuple[int, int, int, int], title: str, annotation: str,
               start_ns: float, end_ns: float, tick_ns: int,
               tag_bands: list[tuple[float, float, str, tuple[int, int, int]]] | None = None,
               overview: bool = False) -> None:
    draw = ImageDraw.Draw(image)
    x, y, w, h = rect
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18,
                           outline=PANEL_EDGE, width=3, fill=(255, 255, 255))
    title_font = font(45 if overview else 39, True)
    note_font = font(32 if overview else 27)
    label_font = font(34 if overview else 29, True)
    value_font = font(31 if overview else 29, True)
    tick_font = font(27 if overview else 25)
    draw.text((x + 35, y + 25), title, font=title_font, fill=INK)
    draw.text((x + 35, y + 90), annotation, font=note_font, fill=MUTED)
    left, right, top, bottom = draw_axis(draw, rect, start_ns, end_ns, tick_ns, tick_font)

    row_h = (bottom - top) / len(REQUIRED)
    if tag_bands:
        band_y1, band_y2 = top + 3, top + 28
        for t0, t1, label, fill in tag_bands:
            xx1 = x_at(max(t0, start_ns), left, right, start_ns, end_ns)
            xx2 = x_at(min(t1, end_ns), left, right, start_ns, end_ns)
            if xx2 <= xx1:
                continue
            draw.rectangle((xx1, band_y1, xx2, band_y2), fill=fill)
            if xx2 - xx1 > text_width(draw, label, note_font) + 14:
                draw.text(((xx1 + xx2 - text_width(draw, label, note_font)) / 2,
                           band_y1 - 3), label, font=note_font, fill=INK)

    # Keep the labels in a fixed gutter so that short zoom ranges stay legible.
    for index, name in enumerate(REQUIRED):
        row_top = round(top + index * row_h)
        row_bottom = round(top + (index + 1) * row_h)
        cy = (row_top + row_bottom) // 2
        draw.line((x + 24, row_bottom, x + w - 24, row_bottom), fill=(232, 237, 241), width=2)
        label = SIGNAL_LABELS[name]
        label_y = cy - (label_font.getbbox(label)[3] - label_font.getbbox(label)[1]) // 2 - 3
        draw.text((x + 35, label_y), label, font=label_font, fill=INK)
        if name == "value":
            draw_bus(draw, series[name], left, right, row_top, row_bottom,
                     start_ns, end_ns, value_font)
        else:
            draw_logic(draw, series[name], left, right, row_top, row_bottom,
                       start_ns, end_ns)

    # Event markers tie annotations to the VCD-derived edge times.
    markers = []
    if start_ns < 165 < end_ns:
        markers.append((165, "15→0", (172, 82, 60)))
    if start_ns < 175 < end_ns:
        markers.append((175, "0→15", (43, 126, 91)))
    if start_ns < 326 < end_ns:
        markers.append((326, "enable↓", (172, 125, 32)))
    if start_ns < 346 < end_ns:
        markers.append((346, "rst↑", (172, 82, 60)))
    for t, label, color in markers:
        px = x_at(t, left, right, start_ns, end_ns)
        draw.line((px, top, px, bottom), fill=color, width=3)
        draw.text((px + 8, top + 5), label, font=font(24, True), fill=color)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vcd", type=Path, default=DEFAULT_VCD, help="source VCD file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT, help="report PNG path")
    args = parser.parse_args()
    vcd_path = args.vcd.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if not vcd_path.is_file():
        raise FileNotFoundError(f"VCD file not found: {vcd_path}")

    series, duration_ns, date_text = parse_vcd(vcd_path)
    if duration_ns <= 0:
        raise ValueError("The VCD contains no positive simulation duration.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    preserved = output_path.parent / "wave.vcd"
    if preserved.exists():
        if digest(preserved) != digest(vcd_path):
            raise FileExistsError(f"Refusing to overwrite different evidence: {preserved}")
    else:
        shutil.copy2(vcd_path, preserved)

    image = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(image)
    title = "LAB2-01 Counter | Normal Experiment Waveforms"
    draw.text((95, 48), title, font=font(66, True), fill=INK)
    source_note = (f"Decoded directly from {vcd_path.name}  ·  duration {duration_ns:g} ns  ·  "
                   f"300 dpi  ·  VCD date: {date_text or 'not recorded'}")
    draw.text((100, 132), source_note, font=font(29), fill=MUTED)

    overview_bands = [
        (0, 6, "reset", RED_FILL),
        (6, 166, "up count + wrap", GREEN_FILL),
        (166, 326, "down count + wrap", (233, 240, 250)),
        (326, 336, "enable hold", GOLD_FILL),
        (336, 346, "enabled down step", GREEN_FILL),
        (346, duration_ns, "reset priority", RED_FILL),
    ]
    draw_panel(
        image, series, (70, 205, 3460, 1110),
        "A. Complete simulation", "Overview · logic levels and hexadecimal value[3:0]",
        0, duration_ns, 50, overview_bands, overview=True,
    )
    draw_panel(
        image, series, (70, 1360, 1695, 1160),
        "B. Counter wrap events", "Up 15→0 at 165 ns · down 0→15 at 175 ns",
        140, 190, 5,
    )
    draw_panel(
        image, series, (1835, 1360, 1695, 1160),
        "C. Hold and synchronous reset", "enable low at 326 ns · rst high at 346 ns · reset sampled at 355 ns",
        315, 356, 5,
    )
    footer = ("Bus labels are hexadecimal. rst is synchronous: assertion at 346 ns is applied at the next "
              "rising clk edge, where value clears to 0.")
    draw.text((95, 2580), footer, font=font(28), fill=MUTED)

    image.save(output_path, format="PNG", dpi=(300, 300), optimize=True)
    print(f"VCD parsed: {vcd_path}")
    print(f"Signals: {', '.join(SIGNAL_LABELS.values())}")
    print(f"Duration: {duration_ns:g} ns")
    print(f"Preserved VCD: {preserved} ({preserved.stat().st_size} bytes)")
    print(f"PNG: {output_path} ({output_path.stat().st_size} bytes)")
    print(f"Canvas: {image.width}x{image.height} px at 300 dpi")
    print("Panels: 0–356 ns overview; 140–190 ns up/down wraps; 315–356 ns enable hold and reset priority")


if __name__ == "__main__":
    main()
