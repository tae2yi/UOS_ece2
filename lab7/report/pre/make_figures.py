"""LAB7 예비보고서 그림 생성기.

- images/vivado/*.png : Vivado 시뮬레이터 화면 캡처(captures/, tools/capture_xsim.ps1)에서
  이름·값 칸과 파형만 잘라 시간축을 반으로 나눠 위아래로 쌓은 것(lab4~lab6과 같은 방식)
- images/theory/*.png : SPI Mode 0 타이밍(MCU 호스트 시뮬레이션의 시각표 CSV를 그대로 그림), FPGA 마스터 상태 순서
- images/block/*.png  : 네 가지 연결(과제9~12)과 FPGA 수신·송신 블록도

모든 그림은 2단 본문의 한 단(약 8 cm)에 들어가므로 폭 1000 px 안팎, 글자 20 px 이상으로 만든다.
그리기 도우미(node, arrow, canvas 등)는 lab6/report/pre/make_figures.py와 같다.

실행: python make_figures.py   (Pillow 필요)
"""
import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
IMG = HERE / 'images'
CAP = HERE / 'captures'
LAB = HERE.parents[1]

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
# (캡처 원본, 신호 행 수) — 2560x1440 전체 화면 캡처 기준 좌표는 lab4~lab6과 같다.
VIVADO = [
    ('lab7_01_spi_rx_tb_view.png', 11), ('lab7_01_spi_rx_tb.png', 10),
    ('lab7_02_spi_tx_tb_view.png', 10), ('lab7_02_spi_tx_tb.png', 10),
    ('lab7_03_spi_link_tb_view.png', 11), ('lab7_03_spi_link_tb.png', 10),
]
NAME_X0, NAME_X1, WAVE_X0, WAVE_MID, WAVE_X1 = 947, 1204, 1208, 1775, 2356
TOP_Y, ROW_Y, ROW_H = 322, 356, 36


def crop_vivado():
    out = IMG / 'vivado'
    out.mkdir(parents=True, exist_ok=True)
    for src, rows in VIVADO:
        if not (CAP / src).is_file():
            continue
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


# ------------------------------------------------------------ drawing helpers
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
        d.rounded_rectangle(box, radius=min(30, (box[3] - box[1]) // 2), fill=LIGHT, outline=(180, 180, 180), width=2)
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


# ------------------------------------------------------------ theory: SPI Mode 0
def read_wave(path, first_n_bytes):
    """hostsim 시각표 CSV(t_ns,cs,sck,mosi)에서 앞의 바이트 n개 구간을 바이트별 (t, cs, sck, mosi) 목록으로"""
    rows = [tuple(int(v) for v in r) for r in csv.reader(open(path, encoding='utf-8')) if r[0].isdigit()]
    out, cur = [], []
    for r in rows:
        cur.append(r)
        if r[1] == 1:               # CS HIGH = 바이트 끝
            out.append(cur)
            cur = []
            if len(out) == first_n_bytes:
                break
    return out


def spi_mode0():
    """0x55와 0xA5 한 바이트씩: CS, SCK, MOSI와 상승 에지에서 읽는 비트"""
    waves = read_wave(LAB / 'stm32_3_hostsim' / 'results' / 'master_wave.csv', 2)
    im, d = canvas(1000, 720)
    f, fb, fs = font(21), font(22, True), font(19)
    left, right = 150, 975
    period = 1280
    t_span = 9 * period + 200          # 바이트 앞뒤 여유 포함
    hi = 46

    def draw_byte(seg, top, value):
        t0 = seg[0][0] - 400
        x_of = lambda t: left + (t - t0) / t_span * (right - left)
        rows = [('CS', 1, top + 70), ('SCK', 2, top + 160), ('MOSI', 3, top + 250)]
        # 대기 상태(바이트 앞): CS 1, SCK 0, MOSI = 첫 비트 앞 값 0
        idle = {1: 1, 2: 0, 3: 0}
        for name, col, y_low in rows:
            d.text((8, y_low - 40), name, font=fb, fill=BLACK)
            path = [(x_of(t0), y_low - hi * idle[col])]
            level = idle[col]
            for r in seg:
                path += [(x_of(r[0]), y_low - hi * level)]
                level = r[col]
                path += [(x_of(r[0]), y_low - hi * level)]
            path.append((x_of(t0 + t_span), y_low - hi * level))
            d.line(path, fill=RED if name == 'MOSI' else NAVY, width=3)
        rises = [r[0] for r in seg if r[2] == 1]
        for i, t in enumerate(rises):
            x = x_of(t)
            d.line([(x, top + 105), (x, top + 265)], fill=(200, 200, 200), width=1)
            bit = next(r[3] for r in seg if r[0] == t)
            d.text((x - 6, top + 268), str(bit), font=f, fill=GREEN)
            d.text((x - 6, top + 20), str(i + 1), font=fs, fill=GRAY)
        d.text((left, top - 8), f'0x{value:02X} — 상승 에지에서 읽은 비트(초록)', font=fs, fill=GRAY)

    draw_byte(waves[0], 20, 0x55)
    draw_byte(waves[1], 350, 0xA5)
    d.text((left, 685), 'SCK 781.25 kHz(주기 1.28 us), 대기 LOW. MOSI는 하강 에지에서 바뀐다.', font=fs, fill=GRAY)
    return im


def spi_master_states():
    """FPGA 마스터(lab7_02) 한 바이트: 반주기(1 µs)마다 상태가 바뀌는 순서"""
    im, d = canvas(1000, 470)
    fb, fs = font(22, True), font(19)
    left, right = 150, 975
    half = 1.0                                    # us
    total = 19 * half                              # LEAD 1 + 8x(H+L) - 마지막 L 대신 TRAIL + GAP
    x_of = lambda t: left + t / total * (right - left)
    value = 0xA5
    bits = [(value >> (7 - i)) & 1 for i in range(8)]
    # 시각표 만들기
    cs = [(0, 0), (17, 1)]
    sck, mosi, states = [], [(0, bits[0])], []
    t = 1
    states.append((0, 1, 'L'))
    for i in range(8):
        sck += [(t, 1), (t + 1, 0)]
        states.append((t, t + 1, 'H'))
        if i < 7:
            mosi.append((t + 1, bits[i + 1]))
            states.append((t + 1, t + 2, 'Lo'))
        t += 2
    states.append((16, 17, 'T'))
    states.append((17, 18, 'G'))
    mosi.append((17, 0))

    def trace(name, pts, y_low, color, init):
        d.text((8, y_low - 40), name, font=fb, fill=BLACK)
        level, path = init, [(x_of(-0.5), y_low - 46 * init)]
        for tt, v in pts:
            path += [(x_of(tt), y_low - 46 * level), (x_of(tt), y_low - 46 * v)]
            level = v
        path.append((x_of(total - 0.5), y_low - 46 * level))
        d.line(path, fill=color, width=3)

    x_of_old = x_of
    x_of = lambda tt: x_of_old(tt + 0.5)
    trace('CS_n', [(0, 0), (17, 1)], 90, NAVY, 1)
    trace('SCK', sck, 180, NAVY, 0)
    trace('MOSI', mosi, 270, RED, 0)
    names = {'L': 'LD', 'H': 'H', 'Lo': 'L', 'T': 'TR', 'G': 'GP'}
    colors = {'L': (250, 230, 200), 'H': PALE, 'Lo': LIGHT, 'T': (250, 230, 200), 'G': (230, 245, 230)}
    for a, b, k in states:
        d.rectangle((x_of(a) + 1, 300, x_of(b) - 1, 345), fill=colors[k], outline=(200, 200, 200))
        label = names[k]
        w = d.textlength(label, font=fs)
        if w < x_of(b) - x_of(a) - 4:
            d.text(((x_of(a) + x_of(b) - w) / 2, 310), label, font=fs, fill=BLACK)
    d.text((8, 310), 'state', font=fb, fill=BLACK)
    for i in range(8):
        x = x_of(1 + 2 * i)
        d.line([(x, 110), (x, 285)], fill=(210, 210, 210), width=1)
    d.text((left, 365), '0xA5 = 1010 0101. 한 칸 = 반주기 50클록(1 us), SCK 500 kHz.', font=fs, fill=GRAY)
    d.text((left, 395), 'LD(LEAD): CS_n LOW와 함께 bit7 준비, 1 us 뒤 첫 상승 에지', font=fs, fill=GRAY)
    d.text((left, 425), 'H/L 8번 반복, 마지막 하강 뒤 TR(TRAIL) 1 us, CS_n HIGH 후 GP(GAP) 1 us', font=fs, fill=GRAY)
    return im


# ------------------------------------------------------------ blocks
def wiring():
    """과제9~12의 네 가지 연결. 송신(마스터) 왼쪽, 수신 오른쪽."""
    im, d = canvas(1000, 700)
    fs, fb = font(19), font(21, True)
    cases = [
        ('과제9  MCU → MCU (옆 조)', ['MCU 마스터', 'ROLE=1'], ['MCU 슬레이브', 'ROLE=2'],
         ['PB3', 'PA7', 'PB6'], ['PB3', 'PA7', 'PA4']),
        ('과제10  MCU → FPGA (자기 조)', ['MCU 마스터', 'ROLE=1'], ['FPGA 수신', 'spi_rx_uart'],
         ['PB3', 'PA7', 'PB6'], ['F8', 'E8', 'A7']),
        ('과제11  FPGA → MCU (자기 조)', ['FPGA 송신', 'spi_tx_uart'], ['MCU 슬레이브', 'ROLE=2'],
         ['F8', 'E8', 'A7'], ['PB3', 'PA7', 'PA4']),
        ('과제12  FPGA → FPGA (옆 조)', ['FPGA 송신', 'spi_tx_uart'], ['FPGA 수신', 'spi_rx_uart'],
         ['F8', 'E8', 'A7'], ['F8', 'E8', 'A7']),
    ]
    sig = ['SCK', 'MOSI', 'CS']
    for k, (title, a, b, pa, pb) in enumerate(cases):
        y = 10 + k * 172
        d.text((10, y), title, font=fb, fill=NAVY)
        node(d, (10, y + 32, 250, y + 160), a + ['VCP: TX=..' if 'MCU' in a[0] else 'UART: TX=..'])
        node(d, (750, y + 32, 990, y + 160), b + ['VCP: RX=..' if 'MCU' in b[0] else 'UART: RX=..'])
        for j in range(3):
            yy = y + 52 + j * 30
            arrow(d, [(330, yy), (670, yy)], color=RED)
            d.text((262, yy - 12), pa[j], font=fs, fill=BLACK)
            d.text((680, yy - 12), pb[j], font=fs, fill=BLACK)
            w = d.textlength(sig[j], font=fs)
            d.rectangle((500 - w / 2 - 4, yy - 12, 500 + w / 2 + 4, yy + 12), fill='white')
            d.text((500 - w / 2, yy - 12), sig[j], font=fs, fill=RED)
        yy = y + 142
        d.line([(330, yy), (670, yy)], fill=GRAY, width=3)
        d.text((262, yy - 12), 'GND', font=fs, fill=GRAY)
        d.text((680, yy - 12), 'GND', font=fs, fill=GRAY)
    return im


def block_rx():
    im, d = canvas(1000, 420)
    node(d, (10, 20, 200, 150), ['BDIO_0~2', 'SCK · MOSI', 'CS_n'], 'port')
    node(d, (250, 10, 500, 160), ['2단 동기화', 'sck_sync', 'mosi · cs_sync'])
    node(d, (550, 10, 990, 160), ['에지 검출 + 시프트', 'sck_s & ~sck_prev', 'bit_count 0~7, CS_n=1이면 0'])
    node(d, (550, 230, 990, 400), ['hex_line_tx + uart_tx', '"RX=" + 16진수 2글자', '+ CR LF, 9600 8N1'])
    node(d, (250, 250, 500, 380), ['led[7:0]', '마지막 바이트'], 'var')
    node(d, (10, 270, 200, 400), ['PC', 'F6 USB-UART'], 'port')
    arrow(d, [(200, 85), (250, 85)])
    arrow(d, [(500, 85), (550, 85)])
    arrow(d, [(770, 160), (770, 230)], 'data · valid', (785, 180))
    arrow(d, [(600, 160), (600, 195), (375, 195), (375, 250)])
    arrow(d, [(550, 380), (200, 380)])
    return im


def block_tx():
    im, d = canvas(1000, 420)
    node(d, (10, 10, 300, 160), ['1초 타이머', 'PERIOD_CLKS', '= 50,000,000'])
    node(d, (360, 10, 640, 160), ['pattern(index)', '55, A5, 00, FF 반복', 'start 1클록'])
    node(d, (700, 10, 990, 160), ['spi_master_tx', 'HALF = 50클록', 'SCK 500 kHz'])
    node(d, (700, 240, 990, 400), ['BDIO_0~2', 'F8 · E8 · A7', '상대 MCU · FPGA로'], 'port')
    node(d, (360, 240, 640, 400), ['hex_line_tx', '"TX=55" + CR LF', 'F6 USB-UART로 PC'])
    node(d, (10, 240, 300, 400), ['led[7:0]', '보낸 바이트'], 'var')
    arrow(d, [(300, 85), (360, 85)], 'tick', (305, 50))
    arrow(d, [(640, 85), (700, 85)])
    arrow(d, [(845, 160), (845, 240)], 'sck·mosi·cs_n', (858, 185))
    arrow(d, [(760, 160), (760, 200), (500, 200), (500, 240)], 'done', (515, 165))
    arrow(d, [(500, 200), (155, 200), (155, 240)])
    return im


def main():
    if CAP.is_dir() and any(CAP.glob('*.png')):
        crop_vivado()
    for folder, name, im in [
        ('theory', 'spi_mode0.png', spi_mode0()),
        ('theory', 'spi_master_states.png', spi_master_states()),
        ('block', 'spi_wiring.png', wiring()),
        ('block', '01_spi_rx_block.png', block_rx()),
        ('block', '02_spi_tx_block.png', block_tx()),
    ]:
        (IMG / folder).mkdir(parents=True, exist_ok=True)
        im.save(IMG / folder / name)
        print(IMG / folder / name)


if __name__ == '__main__':
    main()
