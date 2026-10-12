"""LAB4 결과보고서 그림·측정값 생성기.

videos/*.mp4(보드 실험 영상)에서
- images/board/*.jpg : 보드 사진(영상 장면에 시각과 값을 적은 것)
- data/*.csv         : LED가 바뀐 시각(프레임 단위)과 버튼 클릭음 시각
- images/meas/*.png  : 측정한 LED 타이밍 그림
을 만든다. 타이밍 그림은 예비보고서의 make_figures.timing()을 그대로 쓴다.

실행: python make_figures.py [ffmpeg 경로]   (Pillow, numpy 필요. 경로를 생략하면 PATH의 ffmpeg)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'pre'))
from make_figures import BLACK, GREEN, NAVY, RED, font, timing  # noqa: E402

VID = HERE / 'videos'
IMG = HERE / 'images'
DATA = HERE / 'data'
FFMPEG = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
FPS = 30

FPGA1 = VID / 'lab4_fpga_01_mult_4bit.mp4'
FPGA2 = VID / 'lab4_fpga_02_bcd_conv.mp4'
STM1 = VID / 'lab4_stm32_01_task1_onboard_led.mp4'
STM2 = VID / 'lab4_stm32_02_task2_external_led.mp4'


# ------------------------------------------------------------ 영상 읽기
def grab(video, t):
    """t초 시점의 한 장면."""
    out = subprocess.run([FFMPEG, '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', str(video), '-frames:v', '1',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], stdout=subprocess.PIPE, check=True).stdout
    import io
    return Image.open(io.BytesIO(out)).convert('RGB')


def frames(video, w, h):
    p = subprocess.Popen([FFMPEG, '-loglevel', 'error', '-i', str(video), '-vf', f'scale={w}:{h}',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(int)


def audio(video, rate=16000):
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', str(video), '-ac', '1', '-ar', str(rate),
                          '-f', 's16le', '-'], stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float), rate


# ------------------------------------------------------------ 측정
def edges(on):
    """프레임별 on/off 열 -> [(시각 s, 새 상태)]"""
    return [(i / FPS, int(on[i])) for i in range(1, len(on)) if on[i] != on[i - 1]]


def trace_onboard_led():
    """STM1: 내장 LED LD2(PA5). 항상 켜진 전원 LED(LD3)보다 오른쪽에 있는 초록 화소 수로 판정한다."""
    on = []
    for f in frames(STM1, 1080, 1440):
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        m = (g > 160) & (g - r > 30) & (g - b > 50)
        m[:300] = False
        m[1100:] = False
        xs = np.nonzero(m)[1]
        x0 = np.percentile(xs, 5) if len(xs) else 0
        on.append(int((xs > x0 + 110).sum()) > 40)
    return on


def trace_external_led():
    """STM2: PB0의 외부 적색 LED. 화면 오른쪽 가운데의 밝은 적색 화소 수로 판정한다."""
    on = []
    for f in frames(STM2, 540, 720):
        box = f[250:450, 340:540]
        on.append(int(((box[..., 0] > 235) & (box[..., 0] - box[..., 2] > 60)).sum()) > 60)
    return on


def clicks(video, ratio=20.0):
    """버튼 클릭음: 10 ms 구간의 고역 에너지가 중앙값의 ratio배를 넘는 봉우리의 시각."""
    a, rate = audio(video)
    d = np.diff(a)
    w = rate // 100
    e = np.sqrt((d[:len(d) // w * w].reshape(-1, w) ** 2).mean(1))
    med = np.median(e)
    return [i / 100 for i, v in enumerate(e) if v > ratio * med and v == e[max(0, i - 5):i + 6].max()]


def write_csv(name, on, click):
    rows = [(t, 'LED', v) for t, v in edges(on)] + [(t, 'CLICK', 1) for t in click]
    rows.append((len(on) / FPS, 'END', 0))
    DATA.mkdir(exist_ok=True)
    text = '\n'.join(f'{t:.3f},{sig},{v}' for t, sig, v in sorted(rows))
    (DATA / name).write_text(f'# t_s,signal,value  (LED 초기 상태 {int(on[0])})\n{text}\n', encoding='utf-8')
    print(DATA / name)


# ------------------------------------------------------------ 보드 사진
def sheet(tiles, cols, tile_w, out, label_h=62):
    """tiles: [(Image, 윗줄, 아랫줄)] -> 격자 한 장. 각 장면 위에 두 줄 설명을 적는다."""
    gap = 8
    tile_h = tiles[0][0].height
    rows = -(-len(tiles) // cols)
    im = Image.new('RGB', (cols * tile_w + (cols - 1) * gap, rows * (tile_h + label_h + gap) - gap), 'white')
    d = ImageDraw.Draw(im)
    for i, (tile, top, bottom) in enumerate(tiles):
        x = (i % cols) * (tile_w + gap)
        y = (i // cols) * (tile_h + label_h + gap)
        d.rectangle((x, y, x + tile_w - 1, y + label_h - 1), fill=(234, 242, 248))
        d.text((x + 8, y + 4), top, font=font(23, True), fill=NAVY)
        d.text((x + 8, y + 32), bottom, font=font(21), fill=BLACK)
        im.paste(tile, (x, y + label_h))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=90)
    print(out)


def crop(video, t, box, width):
    im = grab(video, t).crop(box)
    return im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)


def board_fpga1():
    box = (330, 400, 750, 960)
    shots = [(4.0, 'm = 0', '0000_0000'), (5.6, 'm = 1 = 1×1', '0000_0001'), (6.7, 'm = 3 = 3×1', '0000_0011'),
             (7.8, 'm = 7 = 7×1', '0000_0111'), (8.9, 'm = 21 = 7×3', '0001_0101'),
             (9.6, 'm = 77 = 7×11', '0100_1101')]
    sheet([(crop(FPGA1, t, box, 328), f'{t:.1f} s  {a}', f'LED1~8  {b}') for t, a, b in shots], 3, 328,
          IMG / 'board' / 'fpga01_mult.jpg')


def board_fpga2():
    box = (330, 300, 1090, 820)
    shots = [(0.2, '00 → 0', '1 000_0000'), (0.9, '01 → 1', '1 000_0001'), (1.8, '03 → 3', '1 000_0011'),
             (2.9, '07 → 7', '1 000_0111'), (4.5, '27 → 27', '1 001_1011'), (6.1, '67 → 67', '1 100_0011'),
             (6.9, '77 → 77', '1 100_1101'), (8.0, '17 → 17', '1 001_0001'), (10.3, '0, 15 → 무효', '0 000_1111')]
    sheet([(crop(FPGA2, t, box, 328), f'{t:.1f} s  {a}', f'valid bin  {b}') for t, a, b in shots], 3, 328,
          IMG / 'board' / 'fpga02_bcd.jpg')


def board_stm1():
    box = (200, 480, 760, 900)
    shots = [(0.5, '꺼짐', '누르기 전'), (3.0, '켜짐', '첫 누름(1.70 s) 뒤'),
             (6.5, '꺼짐', '5.70 s에 꺼짐'), (8.0, '켜짐', '7.70 s에 켜짐')]
    sheet([(crop(STM1, t, box, 496), f'{t:.1f} s  내장 LED {a}', b) for t, a, b in shots], 2, 496,
          IMG / 'board' / 'stm_task1.jpg')


def board_stm2():
    box = (300, 400, 1060, 970)
    shots = [(0.3, '켜짐', '간격 1 s 구간'), (1.0, '꺼짐', '간격 1 s 구간'),
             (3.4, '꺼짐', '버튼 누름(3.44 s)'), (5.5, '켜짐', '간격 2 s 구간')]
    sheet([(crop(STM2, t, box, 496), f'{t:.1f} s  외부 LED {a}', b) for t, a, b in shots], 2, 496,
          IMG / 'board' / 'stm_task2.jpg')


def board_wiring():
    im = grab(STM1, 4.4).crop((520, 380, 1080, 900))
    im = im.resize((1000, round(1000 * im.height / im.width)), Image.LANCZOS)
    (IMG / 'board').mkdir(parents=True, exist_ok=True)
    im.save(IMG / 'board' / 'stm_wiring.jpg', quality=90)
    print(IMG / 'board' / 'stm_wiring.jpg')


# ------------------------------------------------------------ 타이밍 그림
def model(first_toggle, first_level, interval, presses, end):
    """과제1 코드의 규칙으로 계산한 LED 변화. 간격은 직전 변화 시각부터 세고, 누르면 2배(8초 다음 1초)가 된다."""
    pts, t, level, presses = [(first_toggle, first_level)], first_toggle, first_level, list(presses)
    while True:
        while presses and presses[0] < t + interval:
            p = presses.pop(0)
            interval = 1000 if interval >= 8000 else interval * 2
            if p - t >= interval:                      # 새 간격이 이미 지났으면 누른 직후에 바뀐다
                t, level = p, 1 - level
                pts.append((t, level))
        t += interval
        if t > end:
            return pts
        level = 1 - level
        pts.append((t, level))


def pulses(click_pairs):
    pts = [(0.0, 0)]
    for a, b in click_pairs:
        pts += [(a * 1000, 1), (b * 1000, 0)]
    return pts


def plot_stm(on, click_pairs, led_label, out, with_model):
    end = len(on) / FPS * 1000
    led = [(0.0, int(on[0]))] + [(t * 1000, v) for t, v in edges(on)]
    rows = [('BUTTON\n클릭음', pulses(click_pairs), RED), (led_label + '\n측정', led, NAVY)]
    ts = [t for t, _ in led[1:]]
    spans = [(a, b, f'{(b - a) / 1000:.2f} s', 1) for a, b in zip(ts, ts[1:])]
    if with_model:
        first = led[1]
        rows.append((led_label + '\n계산', [(0.0, 1 - first[1])] + model(first[0], first[1], 1000,
                                                                      [a * 1000 for a, _ in click_pairs], end), GREEN))
    im = timing(rows, 0, end, 2, spans,
                notes=['누름·뗌 클릭음: ' + ', '.join(f'{a:.2f}·{b:.2f} s' for a, b in click_pairs)])
    (IMG / 'meas').mkdir(parents=True, exist_ok=True)
    im.save(IMG / 'meas' / out)
    print(IMG / 'meas' / out)


def main():
    board_fpga1()
    board_fpga2()
    board_stm1()
    board_stm2()
    board_wiring()
    on1, on2 = trace_onboard_led(), trace_external_led()
    c1, c2 = clicks(STM1, 40.0), clicks(STM2)
    write_csv('stm32_task1_led.csv', on1, c1)
    write_csv('stm32_task2_led.csv', on2, c2)
    # 클릭음 가운데 손가락이 버튼 위에 있던 구간의 누름·뗌 쌍(영상으로 확인)
    plot_stm(on1, [(1.70, 1.86), (9.70, 9.89)], 'LED\nPA5', 'stm_task1_timing.png', with_model=False)
    plot_stm(on2, [(3.44, 3.65), (8.08, 8.30)], '외부 LED\nPB0', 'stm_task2_timing.png', with_model=True)


if __name__ == '__main__':
    main()
