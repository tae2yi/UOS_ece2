#!/usr/bin/env python3
"""Render a report-ready digital waveform from a top-level Icarus VCD."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    return ImageFont.truetype(path, size)


def parse_vcd(path: Path, wanted: list[str]):
    scope: list[str] = []
    ids: dict[str, tuple[str, int]] = {}
    scale = None
    in_scale = False
    header = True
    tick = final = 0
    updates: dict[int, dict[str, int | str]] = {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines:
        s = line.strip()
        if header:
            if s.startswith("$scope"):
                scope.append(s.split()[2])
            elif s.startswith("$upscope"):
                scope.pop()
            elif s.startswith("$timescale"):
                rest = s.replace("$timescale", "").replace("$end", "").strip()
                if rest:
                    scale = rest
                else:
                    in_scale = True
            elif in_scale:
                if "$end" in s:
                    scale = ((scale or "") + " " + s.replace("$end", "")).strip()
                    in_scale = False
                else:
                    scale = (scale or "") + " " + s
            elif s.startswith("$var") and len(scope) == 1:
                m = re.match(r"\$var\s+\S+\s+(\d+)\s+(\S+)\s+(\S+)", s)
                if m and m.group(3) in wanted:
                    ids[m.group(2)] = (m.group(3), int(m.group(1)))
            elif s == "$enddefinitions $end":
                header = False
            continue
        if s.startswith("#"):
            tick = int(s[1:])
            final = max(final, tick)
        elif s.startswith("b"):
            parts = s.split()
            if len(parts) == 2 and parts[1] in ids:
                raw = parts[0][1:].lower()
                value = int(raw, 2) if raw and set(raw) <= {"0", "1"} else "X"
                updates.setdefault(tick, {})[ids[parts[1]][0]] = value
        elif s and s[0] in "01xXzZ" and s[1:] in ids:
            updates.setdefault(tick, {})[ids[s[1:]][0]] = int(s[0]) if s[0] in "01" else "X"
    missing = set(wanted) - {n for n, _ in ids.values()}
    if missing:
        raise ValueError(f"Missing top-level VCD signals: {', '.join(sorted(missing))}")
    m = re.search(r"([0-9.]+)\s*(fs|ps|ns|us|ms|s)", scale or "")
    if not m:
        raise ValueError(f"Invalid VCD timescale: {scale!r}")
    unit = {"fs": 1e-6, "ps": 1e-3, "ns": 1, "us": 1e3, "ms": 1e6, "s": 1e9}[m.group(2)]
    ns = float(m.group(1)) * unit
    series = {}
    for name in wanted:
        value: int | str = "X"
        points = []
        for t in sorted(updates):
            if name in updates[t] and updates[t][name] != value:
                value = updates[t][name]
                points.append((t * ns, value))
        series[name] = points
    return series, final * ns


def state_at(points, t):
    value: int | str = "X"
    for pt, v in points:
        if pt > t:
            break
        value = v
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("vcd", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--signals", nargs="+", required=True)
    args = parser.parse_args()
    series, duration = parse_vcd(args.vcd, args.signals)
    if duration <= 0:
        raise ValueError("VCD duration must be positive")

    width, height = 1800, 1150
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    ink, muted, grid, blue = (30, 45, 60), (92, 108, 121), (218, 226, 232), (34, 100, 164)
    draw.text((85, 45), args.title, font=font(48, True), fill=ink)
    draw.text((88, 112), args.note, font=font(27), fill=muted)
    left, right, top = 300, width - 70, 210
    axis_bottom = height - 105
    row_h = (axis_bottom - top) / len(args.signals)
    spacing = 5 if duration <= 30 else 10
    mark = 0
    while mark <= duration:
        x = round(left + mark / duration * (right - left))
        draw.line((x, top - 22, x, axis_bottom), fill=grid, width=2)
        draw.text((x - 22, axis_bottom + 18), f"{mark:g}", font=font(22), fill=muted)
        mark += spacing
    draw.text(((left + right) // 2 - 60, height - 50), "Time (ns)", font=font(24), fill=muted)

    for index, name in enumerate(args.signals):
        y0 = top + index * row_h
        y1 = y0 + row_h
        draw.line((85, y1, right, y1), fill=(235, 239, 242), width=2)
        draw.text((88, (y0 + y1) / 2 - 16), name, font=font(25, True), fill=ink)
        points = series[name]
        is_bus = any(not isinstance(v, int) for _, v in points)
        # The first point may be unknown even if later changes are known; VCD declarations provide widths.
        if name in {"data_in", "stored", "value"} or name in {"count"}:
            is_bus = True
        if is_bus:
            band_top, band_bottom = y0 + 16, y1 - 18
            changes = [(t, v) for t, v in points if 0 < t < duration]
            segments = []
            start, value = 0.0, state_at(points, 0)
            for t, new_value in changes:
                segments.append((start, t, value))
                start, value = t, new_value
            segments.append((start, duration, state_at(points, duration)))
            for a, b, value in segments:
                x1 = round(left + a / duration * (right - left))
                x2 = round(left + b / duration * (right - left))
                if x2 <= x1:
                    continue
                fill = (251, 234, 231) if value == "X" else (230, 240, 248)
                draw.rectangle((x1, band_top, x2, band_bottom), fill=fill, outline=blue, width=3)
                text = "X" if value == "X" else f"{value:X}"
                if x2 - x1 > 35:
                    draw.text(((x1 + x2) / 2 - 12, (band_top + band_bottom) / 2 - 15), text, font=font(24, True), fill=ink)
        else:
            hi, lo = y0 + 18, y1 - 18
            prev_t, value = 0.0, state_at(points, 0)
            for t, new_value in [(t, v) for t, v in points if t > 0] + [(duration, state_at(points, duration))]:
                x1 = round(left + prev_t / duration * (right - left))
                x2 = round(left + t / duration * (right - left))
                y = hi if value == 1 else lo
                draw.line((x1, y, x2, y), fill=blue, width=5)
                if t < duration and new_value != value:
                    new_y = hi if new_value == 1 else lo
                    draw.line((x2, y, x2, new_y), fill=blue, width=5)
                prev_t, value = t, new_value

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, format="PNG", dpi=(220, 220), optimize=True)
    print(f"PNG {args.output} {image.width}x{image.height} px; VCD duration {duration:g} ns")


if __name__ == "__main__":
    main()
