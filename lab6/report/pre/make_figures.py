"""LAB6 예비보고서 그림 생성기.

- images/vivado/*.png : Vivado 시뮬레이터 화면 캡처(captures/, tools/capture_xsim.ps1)에서
  이름·값 칸과 파형만 잘라 시간축을 반으로 나눠 위아래로 쌓은 것(lab4·lab5와 같은 방식)
- images/block/*.png  : 블록 흐름·배선 그림
- images/theory/*.png : UART 프레임, 서보 펄스, DAC 계단 출력의 예상 파형

모든 그림은 2단 본문의 한 단(약 8 cm)에 들어가므로 폭 1000 px 안팎, 글자 20 px 이상으로 만든다.
그리기 도우미(node, arrow, timing 등)는 lab5/report/pre/make_figures.py와 같다.

실행: python make_figures.py   (Pillow 필요)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
IMG = HERE / 'images'
CAP = HERE / 'captures'

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
    ('lab6_01_servo_tb_view.png', 9), ('lab6_01_servo_tb.png', 7),
    ('lab6_02_sram_tb_view.png', 9), ('lab6_02_sram_tb.png', 9),
    ('lab6_03_dac_tb_view.png', 7), ('lab6_03_dac_tb.png', 7),
    ('lab6_04_uart_led_tb_view.png', 8), ('lab6_04_uart_led_tb.png', 8),
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



# ------------------------------------------------------------ STM32_2 blocks
def block_task5():
    im, d = canvas(1000, 300)
    node(d, (10, 20, 230, 130), ['PC', 'Serial Monitor', '9600 8N1'], 'port')
    node(d, (290, 20, 600, 130), ['UART2 (VCP)', 'ST-LINK USB', 'PA2 TX · PA3 RX'])
    node(d, (660, 10, 990, 140), ['polling_routine', 'ch = getchar()', '입력까지 대기'])
    node(d, (660, 180, 990, 290), ['print_byte', '글자 + 0x%02X', 'CR · LF · 그 밖은 ?'], 'var')
    node(d, (290, 180, 600, 290), ['printf', '__io_putchar', 'UART2 송신'])
    arrow(d, [(230, 75), (290, 75)])
    arrow(d, [(600, 75), (660, 75)])
    arrow(d, [(825, 140), (825, 180)])
    arrow(d, [(660, 235), (600, 235)])
    arrow(d, [(290, 235), (120, 235), (120, 130)])
    return im


def block_task67():
    im, d = canvas(1000, 560)
    node(d, (10, 20, 220, 120), ['PC 포트 A', 'MCU VCP'], 'port')
    node(d, (10, 430, 220, 530), ['PC 포트 B', 'FPGA USB-UART'], 'port')
    d.rounded_rectangle((270, 10, 600, 250), radius=12, outline=GRAY, width=2)
    d.text((282, 16), 'NUCLEO-G474RE', font=font(20, True), fill=GRAY)
    node(d, (290, 50, 580, 140), ['getchar', 'UART2 RX'])
    node(d, (290, 160, 580, 240), ['HAL_UART_Transmit', '&huart3, 1 B, 100 ms'])
    d.rounded_rectangle((270, 290, 990, 550), radius=12, outline=GRAY, width=2)
    d.text((282, 296), 'Combo II-DLD · mcu_uart_led', font=font(20, True), fill=GRAY)
    node(d, (660, 330, 970, 420), ['uart_rx', 'BDIO_0 (F8) 입력'])
    node(d, (290, 440, 580, 530), ['uart_tx', 'F6 (USB-UART)'])
    node(d, (660, 440, 970, 530), ["'0' · '1' · '2'", 'led_cmd = LED1'], 'var')
    node(d, (660, 120, 990, 230), ['점퍼선', 'PC10과 F8', 'GND끼리 연결'], 'port')
    arrow(d, [(220, 70), (290, 70)])
    arrow(d, [(435, 140), (435, 160)])
    arrow(d, [(580, 200), (660, 200)], 'PC10', (594, 166), color=RED)
    arrow(d, [(815, 230), (815, 330)], 'UART3 9600 8N1', (826, 265), color=RED)
    arrow(d, [(660, 380), (435, 380), (435, 440)], 'rx_data', (480, 346))
    arrow(d, [(815, 420), (815, 440)])
    arrow(d, [(290, 485), (220, 485)])
    arrow(d, [(290, 105), (220, 105)])
    d.text((14, 135), 'printf: 보낸 바이트,', font=font(19), fill=GRAY)
    d.text((14, 162), '전송 결과', font=font(19), fill=GRAY)
    return im


def block_servo():
    im, d = canvas(1000, 330)
    node(d, (10, 20, 200, 120), ['SW2 · SW3', '왼쪽 · 오른쪽'], 'port')
    node(d, (250, 10, 520, 130), ['button_pulse ×2', '20 ms 안정 확인', '누름당 1클록'])
    node(d, (580, 10, 990, 130), ['servo_position', 'pulse_us 1000~2000', '100씩 증감, 범위 밖 무시'])
    node(d, (450, 190, 830, 320), ['servo_pwm', '20 ms 프레임(1,000,000클록)', 'count < width 이면 HIGH'])
    node(d, (870, 210, 990, 300), ['서보'], 'port')
    arrow(d, [(200, 70), (250, 70)])
    arrow(d, [(520, 70), (580, 70)])
    arrow(d, [(785, 130), (785, 160), (640, 160), (640, 190)], 'pulse_us', (660, 132))
    arrow(d, [(830, 255), (870, 255)])
    d.text((14, 200), '새 폭은 다음', font=font(20), fill=GRAY)
    d.text((14, 230), '프레임부터 적용', font=font(20), fill=GRAY)
    return im


def block_sram():
    im, d = canvas(1000, 360)
    node(d, (10, 20, 220, 120), ['SW2 · SW3', 'ctrl_w · ctrl_r'], 'port')
    node(d, (10, 200, 220, 320), ['DIP 1~8', 'address[3:0]', 'data_in[3:0]'], 'port')
    node(d, (270, 10, 590, 130), ['sram_bus_control', '쓰기·읽기 중 하나만', '동시 요청 무시'])
    node(d, (650, 10, 990, 130), ['/CS · /OE · /WE', '쓰기 0 · 1 · 0', '읽기 0 · 0 · 1'], 'var')
    node(d, (270, 190, 590, 330), ['3상태 버퍼', 'drive_data면 data_in', '아니면 Z'])
    node(d, (650, 190, 990, 330), ['SRAM 256K×16', 'ram_data[15:0]', '읽기: led = [3:0]'], 'port')
    arrow(d, [(220, 70), (270, 70)])
    arrow(d, [(590, 70), (650, 70)])
    arrow(d, [(220, 260), (270, 260)])
    arrow(d, [(430, 130), (430, 190)], 'drive_data', (440, 145))
    arrow(d, [(590, 240), (650, 240)])
    arrow(d, [(650, 290), (590, 290)])
    return im


def block_dac():
    im, d = canvas(1000, 330)
    node(d, (10, 20, 230, 130), ['ramp8', '500,000클록(10 ms)', '마다 value+1'])
    node(d, (300, 10, 640, 140), ['dac_parallel8', 'data = value', '/WR 1클록 LOW'])
    node(d, (700, 20, 990, 130), ['DAC 칩', 'D7~D0 · A/B', '/CS · /LDAC = 0'], 'port')
    node(d, (700, 200, 990, 310), ['전압계 CH0', '계단 모양 상승'], 'port')
    node(d, (300, 200, 640, 310), ['LED1~8', '= dac_d (이진수)'], 'var')
    node(d, (10, 200, 230, 310), ['DIP_SW1', 'add_sel = A/B'], 'port')
    arrow(d, [(230, 75), (300, 75)], 'update', (238, 42))
    arrow(d, [(640, 75), (700, 75)])
    arrow(d, [(845, 130), (845, 200)], 'Vout', (858, 150))
    arrow(d, [(470, 140), (470, 200)])
    arrow(d, [(230, 255), (265, 255), (265, 120), (300, 120)])
    return im


# ------------------------------------------------------------ theory waveforms
def uart_frame():
    """9600 bps 8N1 프레임: 시작 비트, 데이터 D0(LSB)~D7, 정지 비트. 한 비트 104.17 us."""
    im, d = canvas(1000, 420)
    f, fb, fs = font(21), font(22, True), font(19)
    left, right = 150, 970
    bit_w = (right - left) / 12
    labels = ['대기', 'St', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'Sp', '대기']
    for i, lab in enumerate(labels):
        x = left + i * bit_w
        d.line([(x, 30), (x, 330)], fill=(225, 225, 225), width=2)
        d.text((x + bit_w / 2 - d.textlength(lab, font=fs) / 2, 30), lab, font=fs, fill=GRAY)
    for row, (name, sub, value) in enumerate((("'1'", '0x31', 0x31), ("'A'", '0x41', 0x41))):
        bits = [1, 0] + [(value >> k) & 1 for k in range(8)] + [1, 1]
        y_low = 150 + row * 140
        d.text((8, y_low - 58), name, font=fb, fill=BLACK)
        d.text((8, y_low - 30), sub, font=fs, fill=GRAY)
        path = []
        for i, b in enumerate(bits):
            x0, x1 = left + i * bit_w, left + (i + 1) * bit_w
            y = y_low - 60 * b
            path += [(x0, y), (x1, y)]
            if 1 <= i <= 10:
                d.text(((x0 + x1) / 2 - 6, y_low + 6), str(b), font=f, fill=NAVY if 2 <= i <= 9 else RED)
        d.line(path, fill=NAVY, width=3)
    d.text((left, 345), '한 비트 = 1/9600 s = 0.104 ms, 한 문자 10비트 = 1.04 ms', font=fs, fill=GRAY)
    d.text((left, 375), '데이터는 LSB(D0)부터 보낸다. 대기·정지는 HIGH, 시작은 LOW', font=fs, fill=GRAY)
    return im


def servo_pulse():
    rows, spans = [], []
    for i, us in enumerate((1000, 1500, 2000)):
        ms = us / 1000
        rows.append((f'{ms:g} ms\npulse_us={us}', [(0, 1), (ms, 0), (20, 1), (20 + ms, 0)], NAVY))
        spans.append((ms, 20, f'LOW {20 - ms:g} ms', i))
    return timing(rows, 0, 24, 2, spans, unit='ms', axis_label='시간 (ms)',
                  notes=['주기 20 ms(50 Hz). 50 MHz에서 1 ms = 50,000클록',
                         'HIGH 폭 1 · 1.5 · 2 ms가 한쪽 끝 · 가운데 · 반대쪽 끝'])


def dac_ramp():
    pts = [(k * 10.0, (k % 256) / 255) for k in range(0, 600)]
    return timing([('dac_d\n0~255', pts, NAVY)], 0, 6000, 1, [(0, 2560, '2.56 s = 256 × 10 ms', 0)],
                  notes=['10 ms마다 1씩 올라 255 다음 0으로 돌아간다(톱니파)',
                         'Vout ≈ 기준 전압 × dac_d / 256. 기준 전압은 보드에서 확인'])


def main():
    if CAP.is_dir() and any(CAP.glob('*.png')):
        crop_vivado()
    for folder, name, im in [
        ('block', 'stm32_task5_block.png', block_task5()),
        ('block', 'stm32_task67_block.png', block_task67()),
        ('block', '01_servo_block.png', block_servo()),
        ('block', '02_sram_block.png', block_sram()),
        ('block', '03_dac_block.png', block_dac()),
        ('theory', 'uart_frame.png', uart_frame()),
        ('theory', 'servo_pulse.png', servo_pulse()),
        ('theory', 'dac_ramp.png', dac_ramp()),
    ]:
        (IMG / folder).mkdir(parents=True, exist_ok=True)
        im.save(IMG / folder / name)
        print(IMG / folder / name)


if __name__ == '__main__':
    main()
