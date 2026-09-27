#!/usr/bin/env python3
"""Render a report-ready PNG from a top-level testbench VCD."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/System/Library/Fonts/Supplemental/Arial.ttf"] if bold else
        ["/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Helvetica.ttc"]
    )
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def parse_vcd(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    scope: list[str] = []
    signals: dict[str, tuple[str, int]] = {}
    timescale = None
    current_tick = 0
    final_tick = 0
    changes: dict[str, list[tuple[float, int | str]]] = {}
    header = True
    for line in lines:
        value = line.strip()
        if header:
            if value.startswith("$timescale"):
                timescale = value.replace("$timescale", "").replace("$end", "").strip()
            elif value.startswith("$scope"):
                scope.append(value.split()[2])
            elif value.startswith("$upscope"):
                if scope:
                    scope.pop()
            elif value.startswith("$var"):
                parts = value.split()
                if len(parts) >= 5 and len(scope) == 1:
                    signals[parts[3]] = (parts[4], int(parts[2]))
            elif value.startswith("$enddefinitions"):
                header = False
            continue
        if not value or value.startswith("$"):
            continue
        if value.startswith("#"):
            try:
                current_tick = int(value[1:])
                final_tick = max(final_tick, current_tick)
            except ValueError:
                pass
            continue
        ident = None
        decoded: int | str = "X"
        if value[0] in "bB":
            parts = value.split()
            if len(parts) == 2:
                bits, ident = parts[0][1:].lower(), parts[1]
                if bits and set(bits) <= {"0", "1"}:
                    decoded = int(bits, 2)
        elif value[0] in "01xXzZ":
            ident, bit = value[1:], value[0].lower()
            decoded = int(bit) if bit in "01" else "X"
        if ident in signals:
            name, width = signals[ident]
            changes.setdefault(name, []).append((float(current_tick), decoded))

    if not timescale:
        match = re.search(r"\$timescale\s+([^$]+)\$end", text)
        timescale = match.group(1).strip() if match else ""
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(fs|ps|ns|us|ms|s)", timescale)
    if not match:
        raise ValueError(f"Cannot read VCD timescale: {timescale!r}")
    unit_ns = {"fs": 1e-6, "ps": 1e-3, "ns": 1.0, "us": 1e3,
               "ms": 1e6, "s": 1e9}[match.group(2)]
    scale = float(match.group(1)) * unit_ns
    series: dict[str, list[tuple[float, int | str]]] = {}
    widths: dict[str, int] = {}
    for ident, (name, width) in signals.items():
        widths[name] = width
    for name, points in changes.items():
        deduped = []
        prior = object()
        for tick, decoded in points:
            if decoded != prior:
                deduped.append((tick * scale, decoded))
                prior = decoded
        series[name] = deduped
    return series, widths, final_tick * scale


def value_at(points: list[tuple[float, int | str]], time_ns: float) -> int | str:
    current: int | str = "X"
    for timestamp, value in points:
        if timestamp > time_ns:
            break
        current = value
    return current


def bus_text(value: int | str, width: int) -> str:
    if not isinstance(value, int):
        return str(value)
    digits = max(1, math.ceil(width / 4))
    if width > 8:
        return f"{value:0{digits}X}"
    bits = format(value, f"0{width}b")
    return f"{value:0{digits}X}  ({bits})"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("vcd", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--failure-ns", type=float, required=True)
    parser.add_argument("--signals", nargs="+", required=True,
                        help="Top-level VCD signal names, in display order")
    args = parser.parse_args()
    series, widths, end_ns = parse_vcd(args.vcd)
    missing = [name for name in args.signals if name not in series]
    if missing:
        raise SystemExit("Missing VCD signals: " + ", ".join(missing))

    width, height = 3600, 760 + 175 * len(args.signals)
    image = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(image)
    title_font, body_font = font(54, True), font(30)
    label_font, small_font = font(27, True), font(24)
    ink, muted, grid = "#1b2b3a", "#5c6c79", "#d7e0e6"
    blue, fill, edge = "#1f67aa", "#e3eff8", "#2b6391"
    red, red_fill = "#a63f35", "#fae8e4"
    draw.text((110, 60), args.title, font=title_font, fill=ink)
    draw.text((112, 145), args.caption, font=body_font, fill=muted)
    draw.rounded_rectangle((110, 220, width - 110, 325), radius=18,
                           fill=red_fill, outline=red, width=3)
    draw.text((140, 250), f"Expected failure at {args.failure_ns:g} ns", font=label_font,
              fill=red)

    left, right = 430, width - 140
    axis_y = 390
    total = max(end_ns, args.failure_ns) or 1
    end_ns = max(end_ns, args.failure_ns)
    draw.line((left, axis_y, right, axis_y), fill=ink, width=3)
    tick_step = 2 if end_ns <= 20 else 10
    tick = 0
    while tick <= end_ns:
        x = round(left + tick / end_ns * (right - left))
        draw.line((x, axis_y, x, height - 90), fill=grid, width=2)
        draw.line((x, axis_y - 10, x, axis_y + 10), fill=ink, width=3)
        label = f"{tick:g}"
        box = draw.textbbox((0, 0), label, font=small_font)
        draw.text((x - (box[2] - box[0]) / 2, axis_y - 48), label,
                  font=small_font, fill=ink)
        tick += tick_step
    axis_label = "Time (ns)"
    box = draw.textbbox((0, 0), axis_label, font=small_font)
    draw.text(((left + right - box[2] + box[0]) / 2, height - 62),
              axis_label, font=small_font, fill=muted)

    fail_x = round(left + args.failure_ns / end_ns * (right - left))
    draw.line((fail_x, axis_y + 5, fail_x, height - 100), fill=red, width=4)
    for row, name in enumerate(args.signals):
        y = axis_y + 75 + row * 175
        draw.line((110, y + 105, right, y + 105), fill=grid, width=2)
        draw.text((120, y + 32), name, font=label_font, fill=ink)
        points = series[name]
        is_bus = widths[name] > 1
        times = [time for time, _ in points if 0 <= time <= end_ns]
        breaks = sorted(set([0.0, *times, end_ns]))
        for start, stop in zip(breaks, breaks[1:]):
            value = value_at(points, start)
            x1 = round(left + start / end_ns * (right - left))
            x2 = round(left + stop / end_ns * (right - left))
            if is_bus:
                top, bottom = y + 20, y + 92
                draw.polygon([(x1 + 9, top), (x2 - 9, top), (x2, (top + bottom) // 2),
                              (x2 - 9, bottom), (x1 + 9, bottom),
                              (x1, (top + bottom) // 2)], fill=fill, outline=edge)
                label = bus_text(value, widths[name])
                bounds = draw.textbbox((0, 0), label, font=small_font)
                text_width = bounds[2] - bounds[0]
                if x2 - x1 > text_width + 24:
                    draw.text(((x1 + x2 - text_width) / 2, top + 20), label,
                              font=small_font, fill=ink)
            else:
                high_y, low_y = y + 24, y + 91
                trace_y = high_y if value == 1 else low_y if value == 0 else (high_y + low_y) // 2
                trace_color = blue if value in (0, 1) else red
                draw.line((x1, trace_y, x2, trace_y), fill=trace_color, width=5)
                if stop < end_ns:
                    next_value = value_at(points, stop)
                    if value != next_value:
                        next_y = high_y if next_value == 1 else low_y if next_value == 0 else (high_y + low_y) // 2
                        draw.line((x2, trace_y, x2, next_y), fill=blue, width=5)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output)
    print(f"PNG {args.output} ({image.width}x{image.height}), VCD duration={total:g} ns")


if __name__ == "__main__":
    main()
