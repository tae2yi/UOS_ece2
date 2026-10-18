"""LAB5 예비보고서 그림 생성기.

- images/vivado/*.png : Vivado 시뮬레이터 화면 캡처(captures/, tools/capture_xsim.ps1)에서
  이름·값 칸과 파형만 잘라 시간축을 반으로 나눠 위아래로 쌓은 것(lab4와 같은 방식)
- images/hostsim/*.png: stm32_1_hostsim/results/*.csv 를 그린 타이밍 그림
- images/block/*.png  : 블록 흐름 그림

모든 그림은 2단 본문의 한 단(약 8 cm)에 들어가므로 폭 1000 px 안팎, 글자 20 px 이상으로 만든다.
그리기 도우미(node, arrow, timing 등)는 lab4/report/pre/make_figures.py와 같다.

실행: python make_figures.py   (Pillow 필요)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
IMG = HERE / 'images'
CAP = HERE / 'captures'
RESULTS = HERE.parents[1] / 'stm32_1_hostsim' / 'results'

NAVY = (31, 78, 120)
PALE = (234, 242, 248)
GRAY = (110, 110, 110)
LIGHT = (243, 243, 243)
RED = (192, 57, 43)
GREEN = (30, 132, 73)
ORANGE = (200, 120, 20)
BLACK = (34, 34, 34)


def font(size, bold=False):
    name = 'NanumGothic-Bold.ttf' if bold else 'NanumGothic-Regular.ttf'
    for folder in (Path('C:/Windows/Fonts'), Path.home() / 'AppData/Local/Microsoft/Windows/Fonts'):
        if (folder / name).is_file():
            return ImageFont.truetype(str(folder / name), size)
    return ImageFont.truetype('malgunbd.ttf' if bold else 'malgun.ttf', size)


# ------------------------------------------------------------ Vivado crops
# (캡처 원본, 신호 행 수) — 2560x1440 전체 화면 캡처 기준 좌표는 lab4와 같다.
VIVADO = [
    ('lab5_01_piano_tb_view.png', 5), ('lab5_01_piano_tb.png', 5),
    ('lab5_02_traffic_tb_view.png', 11), ('lab5_02_traffic_tb.png', 11),
    ('lab5_03_adc_tb_view.png', 10), ('lab5_03_adc_tb.png', 10),
]
NAME_X0, NAME_X1, WAVE_X0, WAVE_MID, WAVE_X1 = 947, 1204, 1208, 1775, 2356
TOP_Y, ROW_Y, ROW_H = 322, 356, 36


def crop_vivado():
    out = IMG / 'vivado'
    out.mkdir(parents=True, exist_ok=True)
    for src, rows in VIVADO:
        with Image.open(CAP / src) as im:
            if im.size != (2560, 1440):
                raise ValueError(f'{src}: unexpected size {im.size}')
            bottom = ROW_Y + ROW_H * rows + 8
            names = im.crop((NAME_X0, TOP_Y, NAME_X1, bottom))
            halves = [im.crop((WAVE_X0, TOP_Y, WAVE_MID, bottom)), im.crop((WAVE_MID, TOP_Y, WAVE_X1, bottom))]
            sheet = Image.new('RGB', (names.width + max(h.width for h in halves), 2 * names.height + 10), 'white')
            for i, half in enumerate(halves):
                y = i * (names.height + 10)
                sheet.paste(names, (0, y))
                sheet.paste(half, (names.width, y))
            sheet.save(out / src)
        print(out / src)


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
    elif kind == 'var':
        d.rectangle(box, fill='white', outline=ORANGE, width=3)
        text_center(d, box, lines, title_color=ORANGE)
    else:
        d.rounded_rectangle(box, radius=10, fill=PALE, outline=NAVY, width=3)
        text_center(d, box, lines)


def arrow(d, points, label=None, label_at=None, color=NAVY):
    d.line(points, fill=color, width=3)
    (x0, y0), (x1, y1) = points[-2], points[-1]
    if x1 != x0:
        s = 1 if x1 > x0 else -1
        d.polygon([(x1, y1), (x1 - 12 * s, y1 - 7), (x1 - 12 * s, y1 + 7)], fill=color)
    else:
        s = 1 if y1 > y0 else -1
        d.polygon([(x1, y1), (x1 - 7, y1 - 12 * s), (x1 + 7, y1 - 12 * s)], fill=color)
    if label:
        d.text(label_at, label, font=font(19), fill=(60, 60, 60))


def canvas(w, h):
    im = Image.new('RGB', (w, h), 'white')
    return im, ImageDraw.Draw(im)


def block_task3():
    im, d = canvas(1000, 470)
    node(d, (10, 30, 230, 130), ['PC13 상승', 'EXTI15_10'], 'port')
    node(d, (290, 15, 610, 145), ['button_isr_p7', '우선순위 7', '200 ms 안의 호출은 무시'])
    node(d, (680, 25, 990, 135), ['blink_ticks', 'volatile · 10/20/40/80'], 'var')
    node(d, (10, 300, 230, 400), ['TIM6', '100 ms마다'], 'port')
    node(d, (290, 280, 610, 420), ['tim6_isr_p4', '우선순위 4', '++count ≥ blink_ticks?'])
    node(d, (680, 300, 990, 400), ['LED 토글', 'PA5 · count = 0'], 'port')
    arrow(d, [(230, 80), (290, 80)])
    arrow(d, [(610, 80), (680, 80)], '2배', (626, 48), color=ORANGE)
    arrow(d, [(230, 350), (290, 350)])
    arrow(d, [(610, 350), (680, 350)], '예', (634, 318))
    arrow(d, [(835, 135), (835, 205), (450, 205), (450, 280)], '읽기', (640, 172), color=ORANGE)
    d.text((20, 430), 'polling_routine()은 비어 있고, 메인 루프는 아무것도 하지 않는다.', font=font(20), fill=GRAY)
    return im


def block_task4():
    im, d = canvas(1000, 330)
    node(d, (10, 30, 230, 130), ['PC13 상승', 'EXTI15_10'], 'port')
    node(d, (290, 15, 610, 145), ['button_isr_p7', '200 ms 잠금', '+250, 750 다음 250'])
    node(d, (680, 25, 990, 135), ['pwm_compare', 'volatile · 250/500/750'], 'var')
    node(d, (290, 190, 610, 310), ['TIM3 CH1', 'CNT 0~999 (1 MHz)', 'CNT < CCR1 이면 HIGH'])
    node(d, (680, 200, 990, 300), ['PB4', '1 kHz PWM'], 'port')
    arrow(d, [(230, 80), (290, 80)])
    arrow(d, [(610, 80), (680, 80)])
    arrow(d, [(835, 135), (835, 165), (450, 165), (450, 190)])
    d.text((470, 168), '__HAL_TIM_SET_COMPARE', font=font(18), fill=(60, 60, 60))
    arrow(d, [(610, 250), (680, 250)])
    return im


def block_piano():
    im, d = canvas(1000, 260)
    node(d, (10, 75, 210, 185), ['key[7:0]', '버튼 8개'], 'port')
    node(d, (265, 60, 505, 200), ['note_select', '한 개만 HIGH일 때', '262~523 Hz'])
    node(d, (565, 60, 805, 200), ['square_tone', 'CLK / (2f)', '클록마다 토글'])
    node(d, (855, 85, 990, 175), ['piezo'], 'port')
    arrow(d, [(210, 130), (265, 130)])
    arrow(d, [(505, 130), (565, 130)], 'Hz', (520, 98))
    arrow(d, [(805, 130), (855, 130)])
    d.text((265, 222), '여러 키 또는 무입력이면 frequency_hz = 0 (무음)', font=font(20), fill=GRAY)
    return im


def block_traffic():
    im, d = canvas(1000, 330)
    node(d, (10, 20, 220, 110), ['clk_50mhz', 'rst_p'], 'port')
    node(d, (10, 200, 220, 290), ['flicker', '점멸 모드'], 'port')
    node(d, (270, 10, 520, 120), ['second_tick', 'tick: 1초에 1클록', 'blink: 앞 0.5초 HIGH'])
    node(d, (270, 170, 520, 310), ['traffic_sequence', 'phase 0~12 (초)', '12 다음 방향 +1'])
    node(d, (580, 80, 800, 250), ['traffic_lights', '방향별 마스크', 'phase ≤ 10 초록', '11·12 노랑'])
    node(d, (850, 60, 990, 270), ['LED', '차량 R·Y·G', '보행자', 'R·G', '× 4방향'], 'port')
    arrow(d, [(220, 65), (270, 65)])
    arrow(d, [(395, 120), (395, 170)], 'tick', (405, 132))
    arrow(d, [(520, 65), (550, 65), (550, 120), (580, 120)], 'blink', (528, 30))
    arrow(d, [(520, 240), (580, 240)])
    arrow(d, [(220, 245), (270, 245)])
    arrow(d, [(800, 165), (850, 165)])
    return im


def block_adc():
    im, d = canvas(1000, 330)
    node(d, (10, 20, 210, 110), ['add_sel[2:0]', '채널'], 'port')
    node(d, (250, 10, 520, 120), ['adc_command', '채널을 넣은', '16비트 명령'])
    node(d, (250, 170, 540, 310), ['serial_frame16', 'cs_n LOW 동안 16클록', 'SCLK 하강: 송신 · 상승: 수신', 'SCLK 1 MHz'])
    node(d, (665, 170, 990, 310), ['ADC 칩', 'DIN: 명령 입력', 'DOUT: 변환값 출력'], 'port')
    node(d, (640, 10, 990, 120), ['sample[11:0] · led_out', 'rx_word 하위 12비트', 'LED = sample[11:4]'], 'var')
    arrow(d, [(210, 65), (250, 65)])
    arrow(d, [(385, 120), (385, 170)], 'command', (397, 132))
    arrow(d, [(540, 215), (665, 215)], 'SCLK·CS·DIN', (546, 184))
    arrow(d, [(665, 270), (540, 270)], 'DOUT', (570, 278))
    arrow(d, [(500, 170), (500, 145), (600, 145), (600, 65), (640, 65)], 'done', (530, 112))
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
    """디지털 계단 파형. 첫 값 이전은 0으로 본다. 값은 0~1 사이 실수도 된다."""
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


def timing(rows, t0, t1, tick, spans=(), notes=(), unit='s', origin=0.0, width=1000, left=150,
           axis_label=None):
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
        label = f'{t / 1000:g}' if unit == 's' else f'{t - origin:+g}' if origin else f'{t:g}'
        d.text((x - d.textlength(label, font=fs) / 2, axis_y + 6), label, font=fs, fill=GRAY)
        t += step
    axis_label = axis_label or ('시간 (s)' if unit == 's' else '뗀 시각 기준 (ms)')
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


def plot_task3_cycle():
    s, end = load('task3_cycle.csv')
    return timing([('BUTTON\nPC13', s['BUTTON'], RED), ('LED\nPA5', s['PA5'], NAVY)], 0, end, 8,
                  intervals(s['PA5'], 3000, end, 1),
                  notes=['누름 시각: 4.55 s, 10.55 s, 22.55 s, 46.55 s (각 150 ms)',
                         '글자 없는 좁은 구간: 4 s 이전·46 s 이후 1 s, 4~10 s는 2 s'])


def plot_task3_hold_lock():
    h, end_h = load('task3_hold.csv')
    k, end_k = load('task3_lock.csv')
    im1 = timing([('BUTTON\nPC13', h['BUTTON'], RED), ('LED\nPA5', h['PA5'], NAVY)], 0, end_h, 2,
                  intervals(h['PA5'], 0, end_h, 1), notes=['(가) 2.55 s부터 6초 동안 누름: 2초 간격으로 한 번만 바뀜'])
    im2 = timing([('BUTTON\nPC13', k['BUTTON'], RED), ('LED\nPA5', k['PA5'], NAVY)], 0, end_k, 2,
                  intervals(k['PA5'], 0, end_k, 1),
                  notes=['(나) 2.55·2.70 s(150 ms 간격): 두 번째 무시, 2 s',
                         '     5.55·5.85 s(300 ms 간격): 둘 다 인정, 4 s 다음 8 s'])
    im = Image.new('RGB', (1000, im1.height + im2.height), 'white')
    im.paste(im1, (0, 0))
    im.paste(im2, (0, im1.height))
    return im


def plot_task3_bounce():
    a, end = load('task3_bounce.csv')
    b, _ = load('guard3_bounce.csv')
    return timing([('BUTTON\nPC13', a['BUTTON'], RED), ('LED\n과제3 코드', a['PA5'], NAVY),
                   ('LED\n대비안', b['PA5'], GREEN)], 0, end, 2,
                  intervals(a['PA5'], 1900, end, 1) + intervals(b['PA5'], 1900, end, 2),
                  notes=['누름: 2.55 s(150 ms), 6.55 s(1.5 s)', '누를 때와 뗄 때 0.4 ms 간격으로 5번 떨림'])


def pwm_rows(name):
    s, end = load(name)
    pts = [(t, v / 750) for t, v in s['CCR1']]
    labels = []
    ts = [t for t, _ in s['CCR1']] + [end]
    for (t, v), nxt in zip(s['CCR1'], ts[1:]):
        if nxt > t:
            labels.append((t, nxt, f'{v / 10:g} %', 1))
    return s, end, pts, labels


def plot_task4():
    s, end, pts, labels = pwm_rows('task4_pwm.csv')
    return timing([('BUTTON\nPC13', s['BUTTON'], RED), ('PWM 비율\nCCR1/1000', pts, NAVY)], 0, end, 1,
                  labels, notes=['누름 시각: 1.05, 2.05, 3.05, 4.05 s (각 150 ms)',
                                 '높이는 비교값(250·500·750)에 비례'])


def plot_task4_bounce():
    s, end, pts, labels = pwm_rows('task4_pwm_bounce.csv')
    g, _, gpts, glabels = pwm_rows('guard4_pwm_bounce.csv')
    glabels = [(a, b, t, 2) for a, b, t, _ in glabels]
    return timing([('BUTTON\nPC13', s['BUTTON'], RED), ('과제4 코드\nPWM 비율', pts, NAVY),
                   ('대비안\nPWM 비율', gpts, GREEN)], 0, end, 1, labels + glabels,
                  notes=['누름: 1.05 s(150 ms), 2.05 s(1.5 s), 에지마다 5번 떨림'])


def plot_pwm_wave():
    """비교값 250·500·750에서 PB4 파형(TIM3: 1 MHz 카운트, ARR 999, PWM1 모드)"""
    rows = []
    for ccr in (250, 500, 750):
        pts = []
        for k in range(3):
            pts += [(k * 1.0, 1), (k + ccr / 1000, 0)]
        rows.append((f'CCR1={ccr}\n{ccr / 10:g} %', pts, NAVY))
    spans = [(0, 0.25, '0.25 ms', 0), (0, 0.5, '0.5 ms', 1), (0, 0.75, '0.75 ms', 2)]
    return timing(rows, 0, 3, 0.5, spans, unit='ms', axis_label='시간 (ms)',
                  notes=['주기 1 ms(1 kHz). CNT가 CCR1보다 작은 동안 HIGH'])


def main():
    crop_vivado()
    for folder, name, im in [
        ('block', 'stm32_task3_block.png', block_task3()),
        ('block', 'stm32_task4_block.png', block_task4()),
        ('block', '01_piano_block.png', block_piano()),
        ('block', '02_traffic_block.png', block_traffic()),
        ('block', '03_adc_block.png', block_adc()),
        ('hostsim', 'task3_cycle.png', plot_task3_cycle()),
        ('hostsim', 'task3_hold_lock.png', plot_task3_hold_lock()),
        ('hostsim', 'task3_bounce.png', plot_task3_bounce()),
        ('hostsim', 'task4_pwm.png', plot_task4()),
        ('hostsim', 'task4_bounce.png', plot_task4_bounce()),
        ('hostsim', 'pwm_wave.png', plot_pwm_wave()),
    ]:
        (IMG / folder).mkdir(parents=True, exist_ok=True)
        im.save(IMG / folder / name)
        print(IMG / folder / name)


if __name__ == '__main__':
    main()
