"""LAB4 예비보고서 그림 생성기.

- images/vivado/*.png : Vivado 시뮬레이터 화면 캡처(tools/capture_xsim.ps1)에서 파형 영역만 잘라낸 것
- images/hostsim/*.png: stm32_0_hostsim/results/*.csv 를 그린 타이밍 그림
- images/block/*.png  : 블록 흐름·결선 그림

모든 그림은 2단 본문의 한 단(약 8 cm)에 들어가므로 폭 1000 px 안팎, 글자 20 px 이상으로 만든다.

실행: python make_figures.py [캡처 원본 폴더]   (Pillow 필요)
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
IMG = HERE / 'images'
RESULTS = HERE.parents[1] / 'stm32_0_hostsim' / 'results'

NAVY = (31, 78, 120)
PALE = (234, 242, 248)
GRAY = (110, 110, 110)
LIGHT = (243, 243, 243)
RED = (192, 57, 43)
GREEN = (30, 132, 73)
BLACK = (34, 34, 34)


def font(size, bold=False):
    name = 'NanumGothic-Bold.ttf' if bold else 'NanumGothic-Regular.ttf'
    for folder in (Path('C:/Windows/Fonts'), Path.home() / 'AppData/Local/Microsoft/Windows/Fonts'):
        if (folder / name).is_file():
            return ImageFont.truetype(str(folder / name), size)
    return ImageFont.truetype('malgunbd.ttf' if bold else 'malgun.ttf', size)


# ------------------------------------------------------------ Vivado crops
# (원본, 대상, 신호 행 수) — 2560x1440 전체 화면 캡처에서 이름·값 칸과 파형만 남긴다.
# 한 단 폭에서 글자가 읽히도록 시간축을 반으로 잘라 위아래 두 줄로 놓는다. 픽셀은 캡처 그대로다.
VIVADO = [
    ('01_view.png', '01_mult_view.png', 3), ('01_full.png', '01_mult_full.png', 3),
    ('02_view.png', '02_bcd_view.png', 4), ('02_full.png', '02_bcd_full.png', 4),
]
NAME_X0, NAME_X1, WAVE_X0, WAVE_MID, WAVE_X1 = 947, 1204, 1208, 1775, 2356
TOP_Y, ROW_Y, ROW_H = 322, 356, 36


def crop_vivado(src_dir):
    out = IMG / 'vivado'
    out.mkdir(parents=True, exist_ok=True)
    for src, dst, rows in VIVADO:
        with Image.open(Path(src_dir) / src) as im:
            if im.size != (2560, 1440):
                raise ValueError(f'{src}: unexpected size {im.size}')
            bottom = ROW_Y + ROW_H * rows + 8
            names = im.crop((NAME_X0, TOP_Y, NAME_X1, bottom))
            halves = [im.crop((WAVE_X0, TOP_Y, WAVE_MID, bottom)), im.crop((WAVE_MID, TOP_Y, WAVE_X1, bottom))]
            width = names.width + max(h.width for h in halves)
            sheet = Image.new('RGB', (width, 2 * names.height + 10), 'white')
            for i, half in enumerate(halves):
                y = i * (names.height + 10)
                sheet.paste(names, (0, y))
                sheet.paste(half, (names.width, y))
            sheet.save(out / dst)
        print(out / dst)


# ------------------------------------------------------------ block diagrams
def text_center(d, box, lines, title_color=NAVY):
    x0, y0, x1, y1 = box
    fonts = [font(25, True)] + [font(21)] * (len(lines) - 1)
    heights = [f.getbbox('가Ag')[3] + 6 for f in fonts]
    y = (y0 + y1 - sum(heights)) / 2
    for i, (line, f, h) in enumerate(zip(lines, fonts, heights)):
        w = d.textlength(line, font=f)
        d.text(((x0 + x1 - w) / 2, y), line, font=f, fill=title_color if i == 0 else BLACK)
        y += h


def node(d, box, lines, kind='block'):
    if kind == 'port':
        d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=LIGHT, outline=(180, 180, 180), width=2)
        text_center(d, box, lines, title_color=(70, 70, 70))
    else:
        d.rounded_rectangle(box, radius=10, fill=PALE, outline=NAVY, width=3)
        text_center(d, box, lines)


def arrow(d, points, label=None, label_at=None):
    d.line(points, fill=NAVY, width=3)
    (x0, y0), (x1, y1) = points[-2], points[-1]
    if x1 != x0:
        s = 1 if x1 > x0 else -1
        d.polygon([(x1, y1), (x1 - 12 * s, y1 - 7), (x1 - 12 * s, y1 + 7)], fill=NAVY)
    else:
        s = 1 if y1 > y0 else -1
        d.polygon([(x1, y1), (x1 - 7, y1 - 12 * s), (x1 + 7, y1 - 12 * s)], fill=NAVY)
    if label:
        d.text(label_at, label, font=font(19), fill=(60, 60, 60))


def canvas(w, h):
    im = Image.new('RGB', (w, h), 'white')
    return im, ImageDraw.Draw(im)


def block_polling():
    im, d = canvas(1000, 400)
    node(d, (10, 40, 250, 130), ['BUTTON (PC13)', '누르면 HIGH'], 'port')
    node(d, (320, 20, 640, 150), ['누름 검출', '이전 LOW · 현재 HIGH', '직전 인정 후 200 ms 이상'])
    node(d, (720, 20, 990, 150), ['interval_ms', '누름마다 2배', '8000 다음 1000'])
    node(d, (10, 270, 250, 360), ['HAL_GetTick()', '1 ms마다 +1'], 'port')
    node(d, (320, 250, 640, 380), ['경과 비교', 'now - last_toggle', '≥ interval_ms'])
    node(d, (720, 270, 990, 360), ['LED 토글', '과제1 PA5 · 과제2 PB0'], 'port')
    arrow(d, [(250, 85), (320, 85)])
    arrow(d, [(640, 85), (720, 85)], '누름', (660, 56))
    arrow(d, [(250, 315), (320, 315)])
    arrow(d, [(640, 315), (720, 315)], '토글', (660, 286))
    arrow(d, [(855, 150), (855, 200), (480, 200), (480, 250)], '간격', (650, 172))
    return im


def block_mult():
    im, d = canvas(1000, 260)
    node(d, (10, 20, 250, 110), ['a[3:0]', '버스 스위치 4개'], 'port')
    node(d, (10, 150, 250, 240), ['b[3:0]', '버스 스위치 4개'], 'port')
    node(d, (350, 60, 650, 200), ['multiply_unsigned', 'WIDTH = 4', 'product = a * b'])
    node(d, (750, 85, 990, 175), ['m[7:0]', 'LED 8개 · 0~225'], 'port')
    arrow(d, [(250, 65), (300, 65), (300, 105), (350, 105)])
    arrow(d, [(250, 195), (300, 195), (300, 155), (350, 155)])
    arrow(d, [(650, 130), (750, 130)], '8비트', (672, 100))
    return im


def block_bcd():
    im, d = canvas(1000, 260)
    node(d, (10, 20, 250, 110), ['ten[3:0]', '십의 자리 스위치'], 'port')
    node(d, (10, 150, 250, 240), ['one[3:0]', '일의 자리 스위치'], 'port')
    node(d, (340, 45, 660, 215), ['bcd_to_binary', 'binary = ten × 10 + one', 'valid = ten ≤ 9', '그리고 one ≤ 9'])
    node(d, (750, 20, 990, 110), ['bin[6:0]', 'LED 7개 · 0~99'], 'port')
    node(d, (750, 150, 990, 240), ['valid', 'LED 1개'], 'port')
    arrow(d, [(250, 65), (295, 65), (295, 100), (340, 100)])
    arrow(d, [(250, 195), (295, 195), (295, 160), (340, 160)])
    arrow(d, [(660, 100), (705, 100), (705, 65), (750, 65)])
    arrow(d, [(660, 160), (705, 160), (705, 195), (750, 195)])
    return im


def wiring_led():
    im, d = canvas(1000, 230)
    f, fb = font(21), font(25, True)
    y = 105
    node(d, (10, 50, 260, 160), ['PB0', 'GPIO_OUT1_ece2', 'CN7-34 · A3'], 'port')
    d.line([(260, y), (350, y)], fill=NAVY, width=3)
    d.rectangle((350, y - 16, 480, y + 16), fill='white', outline=NAVY, width=3)            # 저항
    d.text((415 - d.textlength('저항', font=fb) / 2, y - 58), '저항', font=fb, fill=NAVY)
    d.text((415 - d.textlength('330 Ω ~ 1 kΩ', font=f) / 2, y + 26), '330 Ω ~ 1 kΩ', font=f, fill=BLACK)
    d.line([(480, y), (580, y)], fill=NAVY, width=3)
    d.polygon([(580, y - 28), (580, y + 28), (630, y)], fill=PALE, outline=NAVY, width=3)   # LED
    d.line([(630, y - 30), (630, y + 30)], fill=NAVY, width=4)
    d.text((605 - d.textlength('LED', font=fb) / 2, y - 70), 'LED', font=fb, fill=NAVY)
    d.text((600 - d.textlength('긴 다리(+)', font=f), y + 44), '긴 다리(+)', font=f, fill=BLACK)
    d.text((612, y + 44), '짧은 다리(-)', font=f, fill=BLACK)
    d.line([(630, y), (760, y)], fill=NAVY, width=3)
    node(d, (760, 50, 990, 160), ['GND', '보드 GND 핀'], 'port')
    return im


# ------------------------------------------------------------ host-sim timing plots
def load(name):
    """CSV -> {신호: [(t_ms, 값), ...]}, 끝 시각(ms)"""
    series, end = {}, 0.0
    for line in (RESULTS / name).read_text().splitlines():
        t, sig, val = line.split(',')
        if sig == 'END':
            end = float(t)
        else:
            series.setdefault(sig, []).append((float(t), int(val)))
    return series, end


def trace(d, pts, x_of, y_low, height, t0, t1, color):
    """디지털 계단 파형. 첫 값 이전은 0으로 본다."""
    level, path = 0, []
    for t, v in pts:
        if t <= t0:
            level = v
    path.append((x_of(t0), y_low - height * level))
    for t, v in pts:
        if t0 < t <= t1:
            path.append((x_of(t), y_low - height * level))
            level = v
            path.append((x_of(t), y_low - height * level))
    path.append((x_of(t1), y_low - height * level))
    d.line(path, fill=color, width=3, joint='curve')


def timing(rows, t0, t1, tick, spans=(), notes=(), unit='s', origin=0.0, width=1000, left=150):
    """rows: [(라벨, 점열, 색)], spans: [(시작 ms, 끝 ms, 글자, 행)] 구간 길이 표시"""
    row_h, top = 110, 50
    h = top + row_h * len(rows) + 66 + 30 * len(notes)
    im, d = canvas(width, h)
    right = width - 30
    f, fb, fs = font(22), font(23, True), font(19)

    def x_of(t):
        return left + (t - t0) / (t1 - t0) * (right - left)

    axis_y = top + row_h * len(rows)
    step = tick * (1000 if unit == 's' else 1)
    t = (int(t0 // step) + (1 if t0 % step else 0)) * step
    while t <= t1 + 1e-6:
        x = x_of(t)
        d.line([(x, top - 16), (x, axis_y)], fill=(225, 225, 225), width=2)
        label = f'{t / 1000:g}' if unit == 's' else f'{t - origin:+g}'
        d.text((x - d.textlength(label, font=fs) / 2, axis_y + 6), label, font=fs, fill=GRAY)
        t += step
    axis_label = '시간 (s)' if unit == 's' else '뗀 시각 기준 (ms)'
    d.text((right - d.textlength(axis_label, font=fs), axis_y + 34), axis_label, font=fs, fill=GRAY)
    for i, (label, pts, color) in enumerate(rows):
        y_low = top + row_h * i + 88
        lines = label.split('\n')
        for j, line in enumerate(lines):
            d.text((8, y_low - 58 + 28 * j - 14 * (len(lines) - 2)), line, font=fb if j == 0 else fs,
                   fill=BLACK if j == 0 else GRAY)
        d.line([(left, y_low), (right, y_low)], fill=(235, 235, 235), width=1)
        trace(d, pts, x_of, y_low, 50, t0, t1, color)
    for a, b, text, row in spans:
        y = top + row_h * row + 18
        d.line([(x_of(a) + 3, y), (x_of(b) - 3, y)], fill=GRAY, width=2)
        for x in (x_of(a) + 3, x_of(b) - 3):
            d.line([(x, y - 7), (x, y + 7)], fill=GRAY, width=2)
        w = d.textlength(text, font=f)
        if w + 14 > x_of(b) - x_of(a):          # 좁은 구간은 눈금만 남긴다
            continue
        cx = (x_of(a) + x_of(b)) / 2
        d.rectangle((cx - w / 2 - 5, y - 14, cx + w / 2 + 5, y + 14), fill='white')
        d.text((cx - w / 2, y - 13), text, font=f, fill=NAVY)
    for j, note in enumerate(notes):
        d.text((left, h - 30 * (len(notes) - j) - 4), note, font=fs, fill=GRAY)
    return im


def intervals(pts, t_from, t_to, row):
    ts = [t for t, _ in pts if t_from <= t <= t_to]
    return [(a, b, f'{(b - a) / 1000:g} s', row) for a, b in zip(ts, ts[1:])]


def plot_cycle(csv, pin, out_label):
    s, end = load(csv)
    led = s[pin]
    return timing([('BUTTON\nPC13', s['BUTTON'], RED), (out_label, led, NAVY)], 0, end, 8,
                  intervals(led, 3000, end, 1),
                  notes=['누름 시각: 4.5 s, 10.5 s, 22.5 s, 46.5 s (각 150 ms)',
                         '글자 없는 좁은 구간: 4 s 이전·46 s 이후 1 s, 4~10 s는 2 s'])


def plot_hold():
    s, end = load('task1_hold.csv')
    return timing([('BUTTON\nPC13', s['BUTTON'], RED), ('LED\nPA5', s['PA5'], NAVY)], 0, end, 2,
                  intervals(s['PA5'], 0, end, 1), notes=['2.5 s부터 8.5 s까지 6초 동안 누름'])


def plot_bounce():
    a, end = load('task1_bounce.csv')
    b, _ = load('guard_bounce.csv')
    return timing([('BUTTON\nPC13', a['BUTTON'], RED), ('LED\n과제1 코드', a['PA5'], NAVY),
                   ('LED\n대비안', b['PA5'], GREEN)], 0, end, 2,
                  intervals(a['PA5'], 1900, end, 1) + intervals(b['PA5'], 1900, end, 2),
                  notes=['누름: 2.5 s(150 ms), 6.5 s(1.5 s)', '누를 때와 뗄 때 0.4 ms 간격으로 5번 떨림'])


def plot_bounce_zoom():
    a, _ = load('task1_bounce.csv')
    return timing([('BUTTON\nPC13', a['BUTTON'], RED)], 7998, 8006, 1, unit='ms', origin=8000,
                  notes=['8.000 s에서 손을 뗄 때의 떨림 모델'])


def plot_examples():
    e1, end1 = load('example1_idle.csv')
    e2, end2 = load('example2_taps.csv')
    im1 = timing([('LED\nPA5', e1['PA5'], NAVY)], 0, end1, 1, intervals(e1['PA5'], 0, end1, 0),
                 notes=['제공 예제 1: 입력 없이 1초마다 상태 변경'])
    im2 = timing([('BUTTON\nPC13', e2['BUTTON'], RED), ('LED\nPA5', e2['PA5'], NAVY)], 0, end2, 1,
                 notes=['제공 예제 2: 누른 순간에만 한 번 변경'])
    im = Image.new('RGB', (1000, im1.height + im2.height), 'white')
    im.paste(im1, (0, 0))
    im.paste(im2, (0, im1.height))
    return im


def main():
    if len(sys.argv) > 1:
        crop_vivado(sys.argv[1])
    for folder, name, im in [
        ('block', 'stm32_polling_block.png', block_polling()),
        ('block', 'stm32_led_wiring.png', wiring_led()),
        ('block', '01_mult_block.png', block_mult()),
        ('block', '02_bcd_block.png', block_bcd()),
        ('hostsim', 'examples.png', plot_examples()),
        ('hostsim', 'task1_cycle.png', plot_cycle('task1_cycle.csv', 'PA5', 'LED\nPA5')),
        ('hostsim', 'task2_cycle.png', plot_cycle('task2_cycle.csv', 'PB0', '외부 LED\nPB0')),
        ('hostsim', 'task1_hold.png', plot_hold()),
        ('hostsim', 'task1_bounce.png', plot_bounce()),
        ('hostsim', 'task1_bounce_zoom.png', plot_bounce_zoom()),
    ]:
        (IMG / folder).mkdir(parents=True, exist_ok=True)
        im.save(IMG / folder / name)
        print(IMG / folder / name)


if __name__ == '__main__':
    main()
