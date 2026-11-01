"""LAB6 결과보고서 그림·측정값 생성기.

videos/*.mp4(보드 실험 영상)에서
- images/board/*.jpg : 보드·화면 사진(영상 장면에 시각과 값을 적은 것)
- images/meas/*.png  : DAC 값 그래프, 과제7 LED 타이밍
- data/*.csv         : 영상에서 읽은 측정값
을 만든다. 손으로 든 휴대전화 영상이라 프레임마다 기준 프레임과의 이동량(위상 상관)을 구해 LED 위치를 보정한다.
서보 팔 각도와 SRAM LED 값, 시리얼 모니터 글자는 장면을 보고 사람이 읽은 값이라 아래 표(SERVO_READ 등)에 적어 둔다.

실행: python make_figures.py [ffmpeg 경로]   (Pillow, numpy 필요. 경로를 생략하면 PATH의 ffmpeg)
"""
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'pre'))
from make_figures import BLACK, GRAY, GREEN, NAVY, RED, canvas, font, timing  # noqa: E402

VID = HERE / 'videos'
IMG = HERE / 'images'
DATA = HERE / 'data'
FFMPEG = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
FPS = 30

SERVO = VID / 'lab6_fpga_01_servo.mp4'
SRAM = VID / 'lab6_fpga_02_sram.mp4'
DAC = VID / 'lab6_fpga_03_dac.mp4'
TASK5 = VID / 'lab6_stm32_01_task5_uart_echo.mp4'
TASK6 = VID / 'lab6_stm32_02_task6_mcu_fpga.mp4'
TASK7 = VID / 'lab6_stm32_03_task7_led_cmd.mp4'

# 장면을 보고 읽은 서보 팔 각도: 보드에 인쇄된 0~180 눈금 기준(90 = 위쪽). (영상 시각 s, 각도, 상태)
SERVO_READ = [(0.1, 90, '시작(리셋 뒤 가운데)'), (1.2, 45, '왼쪽 끝'), (2.0, 90, '가운데'),
              (3.0, 135, '오른쪽 끝'), (4.0, 90, '가운데'), (5.1, 63, '가운데에서 왼쪽으로 3번')]
# 장면을 보고 읽은 SRAM 읽기 결과(LED1~8). 버튼 누름 구간은 클릭음과 손 위치로 정했다.
SRAM_READ = [(5.5, '0000_0011', '첫 번째 읽기'), (11.0, '0000_0010', '두 번째 읽기')]


# ------------------------------------------------------------ 영상 읽기
def grab(video, t):
    out = subprocess.run([FFMPEG, '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', str(video), '-frames:v', '1',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], stdout=subprocess.PIPE, check=True).stdout
    return Image.open(io.BytesIO(out)).convert('RGB')


def frames(video, w, h):
    p = subprocess.Popen([FFMPEG, '-loglevel', 'error', '-i', str(video),
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(float)


def audio(video, rate):
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', str(video), '-ac', '1', '-ar', str(rate),
                          '-f', 's16le', '-'], stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float)


def clicks(video, ratio=8.0, rate=16000):
    """버튼 클릭음: 10 ms 구간의 고역 에너지가 중앙값의 ratio배를 넘는 봉우리의 시각."""
    d = np.diff(audio(video, rate))
    w = rate // 100
    e = np.sqrt((d[:len(d) // w * w].reshape(-1, w) ** 2).mean(1))
    med = np.median(e)
    return [i / 100 for i, v in enumerate(e) if v > ratio * med and v == e[max(0, i - 5):i + 6].max()]


def _shift(a, b):
    """위상 상관으로 a가 b에서 얼마나 움직였는지 (dy, dx)"""
    f = np.fft.fft2(a) * np.conj(np.fft.fft2(b))
    c = np.abs(np.fft.ifft2(f / (np.abs(f) + 1e-9)))
    dy, dx = np.unravel_index(np.argmax(c), c.shape)
    return (dy - c.shape[0] if dy > c.shape[0] // 2 else dy), (dx - c.shape[1] if dx > c.shape[1] // 2 else dx)


def led_trace(video, size, ref_t, box, points, r=9):
    """프레임마다 각 LED 위치(기준 프레임 좌표)의 밝은 빨강 화소 수. 손떨림은 box 영역의 이동량으로 보정."""
    w, h = size
    x0, y0, x1, y1 = box

    def gray(f):
        g = f[y0:y1, x0:x1].mean(2)
        return g - g.mean()

    fs = list(frames(video, w, h))
    ref = gray(fs[round(ref_t * FPS)])
    out = []
    for f in fs:
        dy, dx = _shift(gray(f), ref)
        row = []
        for x, y in points:
            p = f[y + dy - r:y + dy + r, x + dx - r:x + dx + r]
            row.append(int(((p[..., 0] > 200) & (p[..., 1] < 170)).sum()))
        out.append(row)
    return np.array(out)


def write_csv(name, header, rows):
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(header + '\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n',
                             encoding='utf-8')
    print(DATA / name)


# ------------------------------------------------------------ 사진 시트
def sheet(tiles, cols, tile_w, out, label_h=62, sizes=(22, 20)):
    """tiles: [(Image, 윗줄, 아랫줄)] -> 격자 한 장. 각 장면 위에 두 줄 설명을 적는다."""
    gap = 8
    tile_h = max(t[0].height for t in tiles)
    rows = -(-len(tiles) // cols)
    im = Image.new('RGB', (cols * tile_w + (cols - 1) * gap, rows * (tile_h + label_h + gap) - gap), 'white')
    d = ImageDraw.Draw(im)
    for i, (tile, top, bottom) in enumerate(tiles):
        x = (i % cols) * (tile_w + gap)
        y = (i // cols) * (tile_h + label_h + gap)
        d.rectangle((x, y, x + tile_w - 1, y + label_h - 1), fill=(234, 242, 248))
        d.text((x + 8, y + 4), top, font=font(sizes[0], True), fill=NAVY)
        d.text((x + 8, y + 32), bottom, font=font(sizes[1]), fill=BLACK)
        im.paste(tile, (x, y + label_h))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=90)
    print(out)


def crop(video, t, box, width):
    im = grab(video, t).crop(box)
    return im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)


def board_servo():
    box = (180, 330, 740, 770)
    tiles = [(crop(SERVO, t, box, 328), f'{t:.1f} s  약 {a}°', s) for t, a, s in SERVO_READ]
    sheet(tiles, 3, 328, IMG / 'board' / 'fpga01_servo.jpg', sizes=(21, 18))


def board_sram():
    box = (420, 420, 1320, 840)
    shots = [(2.0, 'DIP 설정', '주소·데이터 스위치 조작'), (3.4, 'SW2 쓰기', '버튼 누름, LED 꺼짐'),
             (5.5, 'SW3 읽기', 'LED7·8 켜짐 = 0000_0011'), (7.0, 'DIP 변경', '두 번째 값 설정'),
             (8.3, 'SW2 쓰기', '버튼 누름, LED 꺼짐'), (11.0, 'SW3 읽기', 'LED7 켜짐 = 0000_0010')]
    sheet([(crop(SRAM, t, box, 496), f'{t:.1f} s  {a}', b) for t, a, b in shots], 2, 496,
          IMG / 'board' / 'fpga02_sram.jpg')


def board_dac(values):
    box = (0, 600, 1000, 1000)
    shots = [(0.5, '증가 중'), (1.6, '최댓값 근처'), (1.9, '255 → 0 직후'), (2.3, '다시 증가'),
             (2.87, '모두 꺼짐'), (3.6, '0부터 다시 증가')]
    tiles = []
    for t, what in shots:
        v = values[round(t * FPS)]
        tiles.append((crop(DAC, t, box, 328), f'{t:.1f} s  {what}', f'LED 값 약 {v}' if v is not None else 'LED 0'))
    sheet(tiles, 3, 328, IMG / 'board' / 'fpga03_dac.jpg', sizes=(20, 18))


def board_task5():
    im = crop(TASK5, 12.3, (90, 650, 1080, 900), 1000)
    sheet([(im, '12.3 s  MCU 포트(COM8) 직렬 모니터', "1, 1, a, A 전송 → 0x31, 0x31, 0x61, 0x41")], 1, 1000,
          IMG / 'board' / 'stm_task5.jpg', sizes=(24, 22))


def board_task6():
    a = crop(TASK6, 4.5, (330, 560, 1080, 760), 600)
    b = crop(TASK6, 9.2, (370, 560, 900, 760), 400)
    sheet([(a, '4.5 s  MCU 포트(COM8)', "TX 'a' (0x61), TX LF (0x0A)"),
           (b, '9.2 s  FPGA 포트', '1, a, A 줄마다 수신')], 2, 600,
          IMG / 'board' / 'stm_task6.jpg', sizes=(22, 20))


def board_task7():
    box = (760, 650, 1380, 900)
    shots = [(0.50, "'0' 수신", 'LED1 꺼진 채 유지'), (2.30, "'1' 수신", 'LED2~8 = 011_0001'),
             (3.0, 'LED1 켜짐', 'LF 뒤에도 유지'), (4.17, "'0' 수신", 'LED2~8 = 011_0000'),
             (4.5, 'LED1 꺼짐', 'LF 뒤에도 유지'), (5.5, '끝', 'LED1 꺼짐 유지')]
    sheet([(crop(TASK7, t, box, 496), f'{t:.2f} s  {a}', b) for t, a, b in shots], 2, 496,
          IMG / 'board' / 'stm_task7.jpg')


# ------------------------------------------------------------ DAC: LED 값과 전압계 막대
DAC_LEDS = [(572, 768), (622, 762), (672, 757), (722, 752), (773, 746), (823, 740), (870, 735), (918, 730)]
DAC_BAR = [(x, 851) for x in (10, 33, 56, 79, 102, 125, 148, 172, 196)]


def dac():
    tr = led_trace(DAC, (1080, 1440), 0.5, (300, 500, 1000, 1000), DAC_LEDS + DAC_BAR)
    lit = tr > 60
    n = len(tr)
    ts = np.arange(n) / FPS
    # LED7·8(하위 2비트)은 40·20 ms마다 바뀌어 한 프레임(33 ms) 안에서 섞인다 -> 상위 6비트만 쓰고 가운데 값 +2
    values, rows = [], []
    for i in range(n):
        bits = lit[i, :8]
        if not bits.any():
            v = None                      # 모두 꺼짐 = 0~3
        else:
            v = int(sum(int(b) << (7 - k) for k, b in enumerate(bits[:6]))) + 2
        values.append(v)
        bar = int(lit[i, 8:].sum())
        rows.append((f'{ts[i]:.3f}', ''.join('1' if b else '0' for b in bits), '' if v is None else v, bar))
    write_csv('dac_led_bar.csv', '# t_s,LED1..LED8,value_est(상위 6비트+2),voltage_meter_segments_lit(9개 중)', rows)

    msb = lit[:, 0]
    rise = [ts[i] for i in range(1, n) if msb[i] and not msb[i - 1]]
    fall = [ts[i] for i in range(1, n) if not msb[i] and msb[i - 1]]
    dark = [i for i in range(n) if not lit[i, :6].any() and ts[i] > 2.5]
    reset = (ts[dark[0]], ts[dark[-1]]) if dark else None

    def fit(t0, t1):
        sel = [(ts[i], values[i]) for i in range(n) if t0 <= ts[i] <= t1 and values[i] is not None]
        x, y = np.array(sel).T
        for _ in range(3):                # 잘못 읽은 프레임(잔차 20 이상)을 빼며 다시 맞춘다
            k, c = np.polyfit(x, y, 1)
            keep = np.abs(y - (k * x + c)) < 20
            x, y = x[keep], y[keep]
        return k, c, len(x)

    seg_a = fit(0.0, fall[0] - 0.05)
    seg_b = fit(fall[0] + 0.05, reset[0] - 0.05)
    seg_c = fit(reset[1] + 0.05, ts[-1])
    plot_dac(ts, values, lit[:, 8:].sum(1), [(0.0, fall[0], seg_a), (fall[0], reset[0], seg_b),
                                             (reset[1], ts[-1], seg_c)], reset)
    return values, dict(rise=rise, fall=fall, reset=reset, fits=(seg_a, seg_b, seg_c))


def plot_dac(ts, values, bar, segs, reset):
    W, H = 1000, 700
    left, right, top, h1, gap, h2 = 96, 975, 50, 380, 70, 110
    im, d = canvas(W, H)
    fs, fb = font(19), font(21, True)
    t1 = ts[-1]

    def x_of(t):
        return left + t / t1 * (right - left)

    def y_of(v):
        return top + (1 - v / 256) * h1

    for v in (0, 64, 128, 192, 256):
        d.line([(left, y_of(v)), (right, y_of(v))], fill=(232, 232, 232), width=1)
        d.text((left - 12 - d.textlength(str(v), font=fs), y_of(v) - 11), str(v), font=fs, fill=GRAY)
    d.text((8, top - 40), 'LED1~8 값', font=fb, fill=BLACK)
    for t, v in zip(ts, values):
        if v is not None:
            d.ellipse((x_of(t) - 4, y_of(v) - 4, x_of(t) + 4, y_of(v) + 4), fill=NAVY)
    for a, b, (k, c, _) in segs:
        d.line([(x_of(a), y_of(max(0, k * a + c))), (x_of(b), y_of(min(256, k * b + c)))], fill=GREEN, width=3)
    if reset:
        d.rectangle((x_of(reset[0]), top, x_of(reset[1]) + 2, top + h1), fill=(250, 225, 220))
        d.text((x_of(reset[0]) - 60, top + 8), '모두 꺼짐', font=fs, fill=RED)
    y2 = top + h1 + gap
    d.text((8, y2 - 34), '전압계 막대 (켜진 칸 수)', font=fb, fill=BLACK)
    for v in (0, 9):
        yy = y2 + (1 - v / 9) * h2
        d.line([(left, yy), (right, yy)], fill=(232, 232, 232), width=1)
        d.text((left - 12 - d.textlength(str(v), font=fs), yy - 11), str(v), font=fs, fill=GRAY)
    pts = [(x_of(t), y2 + (1 - b / 9) * h2) for t, b in zip(ts, bar)]
    d.line(pts, fill=RED, width=3)
    for s in range(0, int(t1) + 1):
        d.text((x_of(s) - 5, y2 + h2 + 8), str(s), font=fs, fill=GRAY)
    d.text((right - d.textlength('시간 (s)', font=fs), y2 + h2 + 34), '시간 (s)', font=fs, fill=GRAY)
    d.text((left, H - 26), '점: 프레임마다 읽은 값(상위 6비트), 초록 선: 구간별 직선 맞춤', font=fs, fill=GRAY)
    (IMG / 'meas').mkdir(parents=True, exist_ok=True)
    im.save(IMG / 'meas' / 'dac_value.png')
    print(IMG / 'meas' / 'dac_value.png')


# ------------------------------------------------------------ 과제7: LED1과 받은 바이트
T7_LEDS = [(873, 732), (923, 750), (975, 762), (1032, 775), (1090, 795), (1157, 815), (1226, 832), (1300, 860)]


def task7():
    tr = led_trace(TASK7, (1440, 1080), 3.0, (500, 600, 1400, 1000), T7_LEDS)
    lit = tr > 40
    n = len(tr)
    ts = np.arange(n) / FPS
    rows, events = [], []
    for i in range(n):
        byte = int(sum(int(b) << (6 - k) for k, b in enumerate(lit[i, 1:])))
        rows.append((f'{ts[i]:.3f}', int(lit[i, 0]), f'{byte:07b}', f'0x{byte:02X}'))
        if byte != 0x0A:
            events.append((ts[i], byte))
    write_csv('stm32_task7_led.csv', '# t_s,LED1(led_cmd),LED2..LED8(led_byte),byte', rows)
    led1 = lit[:, 0]
    edges = [(ts[i], int(led1[i])) for i in range(1, n) if led1[i] != led1[i - 1]]
    cmd = [(0.0, 0)] + [(t * 1000, v) for t, v in edges]
    # 받은 바이트가 LF가 아닌 프레임을 펄스로
    rx, prev = [(0.0, 0)], 0
    for i in range(n):
        cur = int(rows[i][3] != '0x0A')
        if cur != prev:
            rx.append((ts[i] * 1000, cur))
            prev = cur
    # 한 프레임(33 ms) 안에 문자와 뒤따르는 LF가 함께 찍혀 두 바이트의 OR로 보인다 -> LF 비트를 지우면 문자
    first = [(t, b) for k, (t, b) in enumerate(events) if k == 0 or t - events[k - 1][0] > 0.1]
    spans = [(t * 1000 - 220, t * 1000 + 220, f"'{chr(b & ~0x0A)}'", 0) for t, b in first]
    im = timing([('LED2~8\nLF 아닌 바이트', rx, RED), ('LED1\nled_cmd', cmd, NAVY)],
                0, ts[-1] * 1000, 1, spans,
                notes=['LED2~8은 마지막 받은 바이트. 문자 뒤에 LF(0x0A)가 따라와 대부분 000_1010을 보인다'])
    im.save(IMG / 'meas' / 'stm_task7_timing.png')
    print(IMG / 'meas' / 'stm_task7_timing.png')
    return edges, events


# ------------------------------------------------------------ 서보·SRAM 읽은 값
def manual_tables():
    write_csv('servo_angle_readout.csv', '# t_s,angle_deg,state  (보드 눈금을 보고 읽은 값, 90 = 위쪽)', SERVO_READ)
    write_csv('servo_clicks.csv', '# t_s  (영상 음성의 버튼 클릭음)', [(t,) for t in clicks(SERVO)])
    write_csv('sram_led_readout.csv', '# t_s,LED1..LED8,action  (장면을 보고 읽은 값)', SRAM_READ)


def main():
    values, info = dac()
    print('dac', {k: v for k, v in info.items()})
    board_dac(values)
    print('task7', task7())
    manual_tables()
    board_servo()
    board_sram()
    board_task5()
    board_task6()
    board_task7()


if __name__ == '__main__':
    main()
