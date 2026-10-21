"""LAB5 결과보고서 그림·측정값 생성기.

videos/*.mp4(보드 실험 영상)에서
- images/board/*.jpg : 보드 사진(영상 장면에 시각과 값을 적은 것)
- images/meas/*.png  : 피아노 소리 스펙트로그램, 신호등·과제3 타이밍 그림
- data/*.csv         : 영상·음성에서 읽은 측정값
을 만든다. 타이밍 그림은 예비보고서의 make_figures.timing()을 그대로 쓴다.
ADC LED 값과 오실로스코프 듀티비 표시는 장면을 보고 사람이 읽은 값이라 아래 표(ADC_READ, PWM_READ)에 적어 둔다.

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

PIANO = VID / 'lab5_fpga_01_piano.mp4'
TRAFFIC = VID / 'lab5_fpga_02_traffic.mp4'
ADC = VID / 'lab5_fpga_03_adc.mp4'
TASK3 = VID / 'lab5_stm32_01_task3_led_interval.mp4'
TASK4 = VID / 'lab5_stm32_02_task4_pwm.mp4'

NOTES = [('도', 'C4', 262), ('레', 'D4', 294), ('미', 'E4', 330), ('파', 'F4', 349),
         ('솔', 'G4', 392), ('라', 'A4', 440), ('시', 'B4', 494), ('높은 도', 'C5', 523)]

# 장면을 보고 읽은 값. (영상 시각 s, 채널, 켜진 LED 번호, 손의 조작)
ADC_READ = [(0.5, 0, (1, 2, 3, 5, 6, 7), '휴대전화를 CdS 위에 댐'),
            (2.5, 0, (1, 2, 3, 7), '휴대전화를 CdS 위에 댐'),
            (3.0, 0, (1, 2, 3, 7), '휴대전화를 CdS 위에 댐'),
            (5.8, 1, (), 'DIP_SW1 전환 직후, 가변저항'),
            (6.5, 1, (5, 7), '가변저항을 돌림'),
            (7.0, 1, (3, 4), '가변저항을 돌림'),
            (9.0, 1, (1, 2, 3, 6, 7), '가변저항을 돌림'),
            (12.0, 1, (1, 3, 4, 6, 7), '가변저항을 돌림'),
            (17.0, 1, (1, 2, 3, 4, 5, 6, 7), '가변저항을 돌림')]
# 오실로스코프 측정 표시(CH1 포지티브 듀티 사이클)를 0.2 s 간격 장면에서 읽은 값
PWM_READ = [(1.6, 50.00), (1.8, 50.00), (2.0, 50.00), (2.2, 74.90), (2.4, 75.00), (2.6, 75.00), (2.8, 75.00),
            (3.0, 75.24), (3.2, 75.24), (3.4, 74.99), (3.6, 74.99), (3.8, 24.99), (4.0, 24.99), (4.2, 24.99),
            (4.4, 24.99), (4.6, 24.99), (4.8, 24.99), (5.0, 25.00), (5.4, 49.84), (5.6, 49.83), (5.8, 49.83),
            (6.0, 49.90), (6.2, 50.00), (6.4, 50.00), (6.6, 74.99), (6.8, 74.91)]


# ------------------------------------------------------------ 영상 읽기
def grab(video, t):
    out = subprocess.run([FFMPEG, '-loglevel', 'error', '-ss', f'{t:.3f}', '-i', str(video), '-frames:v', '1',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], stdout=subprocess.PIPE, check=True).stdout
    return Image.open(io.BytesIO(out)).convert('RGB')


def frames(video, w, h):
    p = subprocess.Popen([FFMPEG, '-loglevel', 'error', '-i', str(video), '-vf', f'scale={w}:{h}',
                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(int)


def audio(video, rate):
    raw = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', str(video), '-ac', '1', '-ar', str(rate),
                          '-f', 's16le', '-'], stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(float)


def edges(on):
    """프레임별 on/off 열 -> [(시각 s, 새 상태)]"""
    return [(i / FPS, int(on[i])) for i in range(1, len(on)) if on[i] != on[i - 1]]


def clicks(video, ratio=10.0, rate=16000):
    """버튼 클릭음: 10 ms 구간의 고역 에너지가 중앙값의 ratio배를 넘는 봉우리의 시각."""
    d = np.diff(audio(video, rate))
    w = rate // 100
    e = np.sqrt((d[:len(d) // w * w].reshape(-1, w) ** 2).mean(1))
    med = np.median(e)
    return [i / 100 for i, v in enumerate(e) if v > ratio * med and v == e[max(0, i - 5):i + 6].max()]


def write_csv(name, header, rows):
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(header + '\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n',
                             encoding='utf-8')
    print(DATA / name)


# ------------------------------------------------------------ 보드 사진
def sheet(tiles, cols, tile_w, out, label_h=62, sizes=(23, 21)):
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
        d.text((x + 8, y + 4), top, font=font(sizes[0], True), fill=NAVY)
        d.text((x + 8, y + 32), bottom, font=font(sizes[1]), fill=BLACK)
        im.paste(tile, (x, y + label_h))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=90)
    print(out)


def crop(video, t, box, width):
    im = grab(video, t).crop(box)
    return im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)


def board_piano(notes):
    box = (640, 330, 1520, 1080)
    times = [1.35, 1.78, 2.20, 2.67, 3.00, 3.58, 4.15, 4.70]
    tiles = []
    for t, (ko, en, f0), meas in zip(times, NOTES, notes):
        tiles.append((crop(PIANO, t, box, 246), f'{t:.1f} s  {ko}', f'측정 {meas:.1f} Hz'))
    sheet(tiles, 4, 246, IMG / 'board' / 'fpga01_piano.jpg', sizes=(21, 19))


def board_traffic():
    box = (330, 400, 920, 840)
    shots = [(0.4, '점멸 모드', 'SW2 누름: 노랑·보행 빨강'), (2.5, '방향 0, phase 1~2', '서쪽 차량·보행 초록'),
             (4.8, 'phase 4 뒤반', '보행 초록 꺼짐(점멸)'), (5.4, 'phase 5 앞반', '보행 초록 켜짐(점멸)'),
             (12.0, 'phase 11~12', '노랑, 보행 빨강'), (15.0, '방향 1, phase 1~2', '동쪽 차량·보행 초록')]
    sheet([(crop(TRAFFIC, t, box, 328), f'{t:.1f} s  {a}', b) for t, a, b in shots], 3, 328,
          IMG / 'board' / 'fpga02_traffic.jpg', sizes=(21, 19))


def led_bits(on):
    return ''.join('1' if i in on else '0' for i in range(1, 9))


def board_adc():
    box = (250, 270, 1100, 650)
    pick = [0, 2, 3, 4, 6, 8]
    tiles = []
    for k in pick:
        t, ch, on, _ = ADC_READ[k]
        b = led_bits(on)
        tiles.append((crop(ADC, t, box, 328), f'{t:.1f} s  ch{ch} {"CdS" if ch == 0 else "가변저항"}',
                      f'LED {b[:4]}_{b[4:]}'))
    sheet(tiles, 3, 328, IMG / 'board' / 'fpga03_adc.jpg', sizes=(21, 19))


def board_task3():
    box = (230, 640, 850, 1260)
    shots = [(0.5, '꺼짐', '시작'), (1.0, '켜짐', '0.79 s에 켜짐'), (1.8, '손가락', '첫 누름 구간'),
             (3.0, '꺼짐', '간격 2 s 구간'), (4.5, '켜짐', '3.88 s에 켜짐'), (7.3, '손가락', '두 번째 누름'),
             (9.5, '꺼짐', '5.91 s부터 꺼짐'), (12.0, '켜짐', '11.38 s에 켜짐')]
    sheet([(crop(TASK3, t, box, 246), f'{t:.1f} s  LD2 {a}', b) for t, a, b in shots], 4, 246,
          IMG / 'board' / 'stm_task3.jpg', sizes=(20, 18))


def board_task4():
    box = (140, 260, 1010, 770)
    shots = [(1.8, '50 %', '듀티 표시 50.00 %'), (2.6, '75 %', '듀티 표시 75.00 %'),
             (4.2, '25 %', '듀티 표시 24.99 %'), (6.2, '50 %', '듀티 표시 50.00 %')]
    sheet([(crop(TASK4, t, box, 496), f'{t:.1f} s  CH1(PB4) {a}', b) for t, a, b in shots], 2, 496,
          IMG / 'board' / 'stm_task4_scope.jpg')


# ------------------------------------------------------------ 피아노: 소리에서 음높이
def note_segments(a, rate):
    """50 ms마다 여덟 음의 홀수 고조파 크기 합을 비교해, 한 음이 뚜렷한 구간을 찾는다."""
    n, hop = rate // 10, rate // 20
    f = np.fft.rfftfreq(n, 1 / rate)
    win = np.hanning(n)
    best = []
    for s in range(0, len(a) - n, hop):
        sp = np.abs(np.fft.rfft(a[s:s + n] * win))
        bg = np.median(sp[(f > 1000) & (f < 6000)]) + 1
        sc = []
        for _, _, f0 in NOTES:
            k = [int(round(h * f0 * n / rate)) for h in range(1, 16, 2) if 900 < h * f0 < 6000]
            sc.append(sum(sp[i - 1:i + 2].max() / bg for i in k))
        i = int(np.argmax(sc))
        best.append((s / rate, s / rate + n / rate, i if sc[i] > 60 else None))
    segs = []
    for t0, t1, i in best:
        if i is None:
            continue
        if segs and segs[-1][2] == i and t0 <= segs[-1][1]:
            segs[-1][1] = t1
        else:
            segs.append([t0, t1, i])
    return [s for s in segs if s[1] - s[0] >= 0.15]   # 0.1 s짜리 잡음 구간은 버린다


def note_freq(seg, f_nom, rate):
    """구간에서 가장 센 홀수 고조파의 정확한 주파수(포물선 보간)를 고조파 차수로 나눈다."""
    n = 1 << 18
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n))
    best = None
    for h in range(3, 16, 2):
        if not 1500 < h * f_nom < 4500:
            continue
        k0 = int(h * f_nom * 0.99 * n / rate)
        k1 = int(h * f_nom * 1.01 * n / rate)
        k = k0 + int(np.argmax(sp[k0:k1]))
        if best is None or sp[k] > best[0]:
            y0, y1, y2 = np.log(sp[k - 1:k + 2])
            best = (sp[k], (k + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)) * rate / n / h, h)
    return best[1], best[2]


def piano():
    rate = 48000
    a = audio(PIANO, rate)
    segs = note_segments(a, rate)
    rows, meas = [], []
    for t0, t1, i in segs:
        ko, en, f0 = NOTES[i]
        half = 50_000_000 // (2 * f0)
        f_design = 50_000_000 / (2 * half)
        f, h = note_freq(a[int(t0 * rate):int(t1 * rate)], f0, rate)
        rows.append((f'{t0:.2f}', f'{t1:.2f}', en, f0, f'{f_design:.3f}', f'{f:.2f}', h))
        meas.append(f)
    write_csv('piano_notes.csv', '# t_start_s,t_end_s,note,target_hz,design_hz,measured_hz,harmonic_used', rows)
    plot_spectrogram(a, rate, segs)
    return meas


def plot_spectrogram(a, rate, segs, f_lo=1800, f_hi=3300, t_end=5.4):
    n, hop = 4096, 480
    win = np.hanning(n)
    f = np.fft.rfftfreq(n, 1 / rate)
    band = (f >= f_lo) & (f <= f_hi)
    cols = []
    for s in range(0, int(t_end * rate) - n, hop):
        cols.append(20 * np.log10(np.abs(np.fft.rfft(a[s:s + n] * win))[band] + 1))
    S = np.array(cols).T[::-1]
    lo, hi = np.percentile(S, 60), S.max()
    S = np.clip((S - lo) / (hi - lo), 0, 1)
    W, H, left, top, plot_h = 1000, 560, 96, 70, 400
    im, d = canvas(W, H)
    img = np.stack([255 - S * (255 - c) for c in NAVY], -1).astype(np.uint8)
    spec = Image.fromarray(img).resize((W - left - 20, plot_h), Image.BILINEAR)
    im.paste(spec, (left, top))
    fs, fb = font(19), font(21, True)

    def x_of(t):
        return left + t / (len(cols) * hop / rate) * (W - left - 20)

    def y_of(fr):
        return top + (f_hi - fr) / (f_hi - f_lo) * plot_h

    for fr in range(2000, 3301, 250):
        d.line([(left - 6, y_of(fr)), (left, y_of(fr))], fill=GRAY, width=2)
        d.text((left - 12 - d.textlength(str(fr), font=fs), y_of(fr) - 11), str(fr), font=fs, fill=GRAY)
    for t in range(0, 6):
        if x_of(t) <= W - 20:
            d.text((x_of(t) - 5, top + plot_h + 6), str(t), font=fs, fill=GRAY)
    d.text((W - 20 - d.textlength('시간 (s)', font=fs), top + plot_h + 32), '시간 (s)', font=fs, fill=GRAY)
    d.text((8, top - 46), '주파수 (Hz)', font=fs, fill=GRAY)
    for t0, t1, i in segs:
        ko, en, f0 = NOTES[i]
        x = (x_of(t0) + x_of(t1)) / 2
        d.text((x - d.textlength(en, font=fb) / 2, top - 30), en, font=fb, fill=RED)
    d.text((left, H - 28), '피에조 소리의 고조파(기본 주파수의 4~13배)가 보이는 대역. 음 이름은 고조파 간격으로 판정했다.',
           font=fs, fill=GRAY)
    (IMG / 'meas').mkdir(parents=True, exist_ok=True)
    im.save(IMG / 'meas' / 'piano_spectrogram.png')
    print(IMG / 'meas' / 'piano_spectrogram.png')


# ------------------------------------------------------------ 신호등
def trace_traffic():
    """서쪽(왼쪽)과 동쪽(오른쪽) 보행 신호의 초록 화소 수로 켜짐을 판정한다."""
    west, east = [], []
    for f in frames(TRAFFIC, 540, 720):
        box = f[200:420, 165:460]
        r, g = box[..., 0], box[..., 1]
        xs = np.nonzero((g > 140) & (g - r > 40))[1]
        west.append(int((xs < 145).sum()) > 1000)
        east.append(int((xs >= 145).sum()) > 1000)
    return west, east


def traffic_model(t, release, tick0):
    """설계 규칙: flicker를 뗀 뒤 tick마다 phase가 1씩, 13초마다 방향이 바뀐다. blink는 tick 뒤 0.5 s 동안 HIGH."""
    if t < release:
        return 0, 0
    ticks = int(np.floor(t - tick0)) - int(np.floor(release - tick0))
    direction, phase = divmod(ticks, 13)
    blink = (t - tick0) % 1.0 < 0.5
    walk = phase <= 3 or (phase <= 10 and blink)
    return int(direction == 0 and walk), int(direction == 1 and walk)


def traffic():
    west, east = trace_traffic()
    end = len(west) / FPS
    ew, ee = edges(west), edges(east)
    rows = [(f'{t:.3f}', 'WEST_WALK_GREEN', v) for t, v in ew] + [(f'{t:.3f}', 'EAST_WALK_GREEN', v) for t, v in ee]
    write_csv('traffic_walk_green.csv', '# t_s,signal,value  (두 신호 모두 0에서 시작)', sorted(rows, key=lambda r: float(r[0])))
    # 기준: 첫 점멸 꺼짐(phase 4의 blink 하강)이 tick + 0.5 s. flicker 해제는 서쪽 초록이 처음 켜진 프레임.
    tick0 = ew[1][0] - 0.5
    release = ew[0][0] - 1 / FPS / 2
    ts = np.arange(0, end, 1 / 300)
    calc = [traffic_model(t, release, tick0) for t in ts]

    def pts(seq):
        out = [(0.0, seq[0])]
        out += [(ts[i] * 1000, seq[i]) for i in range(1, len(seq)) if seq[i] != seq[i - 1]]
        return out

    meas_w = [(0.0, 0)] + [(t * 1000, v) for t, v in ew]
    meas_e = [(0.0, 0)] + [(t * 1000, v) for t, v in ee]
    im = timing([('서쪽 보행\n측정', meas_w, NAVY), ('서쪽 보행\n계산', pts([c[0] for c in calc]), GREEN),
                 ('동쪽 보행\n측정', meas_e, NAVY), ('동쪽 보행\n계산', pts([c[1] for c in calc]), GREEN)],
                0, end * 1000, 2,
                notes=[f'계산 기준: flicker 해제 {release:.2f} s, tick {tick0 % 1:.3f} + n s (첫 점멸 꺼짐에서 구함)'])
    im.save(IMG / 'meas' / 'traffic_timing.png')
    print(IMG / 'meas' / 'traffic_timing.png')
    # 측정 변화 시각과 계산 변화 시각의 차
    cw = [t / 1000 for t, _ in pts([c[0] for c in calc])[1:]]
    ce = [t / 1000 for t, _ in pts([c[1] for c in calc])[1:]]
    diffs = [m - c for (m, _), c in zip(ew, cw)] + [m - c for (m, _), c in zip(ee, ce)]
    return ew, ee, tick0, release, max(abs(x) for x in diffs[2:])


# ------------------------------------------------------------ 과제3
def trace_task3():
    """내장 LED LD2(PA5): 리셋·사용자 버튼 사이의 밝은 초록 화소 수. 손가락이 가린 프레임은 None."""
    on = []
    for f in frames(TASK3, 540, 720):
        box = f[340:475, 210:320]
        r, g, b = box[..., 0], box[..., 1], box[..., 2]
        skin = ((r > 170) & (r - b > 50) & (g > 110)).sum()
        lit = ((g > 170) & (g - r > 25) & (g - b > 60)).sum() > 8
        on.append(None if skin > 300 else lit)
    return on


def task3():
    on = trace_task3()
    end = len(on) / FPS
    ev, seen, prev, hidden = [], [], on[0], []     # ev: 변화가 보인 프레임, seen: 가려진 사이에 바뀐 것
    for i, v in enumerate(on):
        if v is None:
            if not hidden or hidden[-1][1] != i - 1:
                hidden.append([i, i])
            hidden[-1][1] = i
            continue
        if v != prev:
            (seen if hidden and hidden[-1][1] == i - 1 else ev).append((i / FPS, int(v)))
        prev = v
    c = clicks(TASK3)
    rows = [(f'{t:.3f}', 'LED', v) for t, v in ev] + [(f'{t:.2f}', 'CLICK', 1) for t in c]
    rows += [(f'{t:.3f}', 'LED_AFTER_HIDDEN', v) for t, v in seen]
    rows += [(f'{a / FPS:.3f}', 'HIDDEN_FROM', 1) for a, b in hidden] + [(f'{b / FPS:.3f}', 'HIDDEN_TO', 1) for a, b in hidden]
    write_csv('stm32_task3_led.csv', '# t_s,signal,value  (LED 초기 상태 0, HIDDEN = 손가락이 LED를 가린 구간)',
              sorted(rows, key=lambda r: float(r[0])))
    on_t = [t for t, v in ev if v == 1]
    first = on_t[0]
    # 코드의 규칙: 간격은 직전 변화부터, 누르면 2배. 첫 누름은 1.79 s 변화 뒤, 두 번째는 7.79 s 변화 전.
    calc = [(first, 1), (first + 1, 0), (first + 3, 1), (first + 5, 0), (first + 9, 1)]
    # 가려진 사이의 변화는 가려지기 시작한 시각에 그린다(실제 시각은 그 구간 안 어딘가)
    shown = ev + [(hidden[0][0] / FPS, v) for t, v in seen if hidden[0][1] / FPS < t < hidden[0][1] / FPS + 0.1]
    led = [(0.0, 0)] + [(t * 1000, v) for t, v in sorted(shown)]
    cpts = [(0.0, 0)] + [(t * 1000, v) for t, v in calc if t < end]
    press = [(0.0, 0), (hidden[0][0] / FPS * 1000, 1), (hidden[0][1] / FPS * 1000, 0)]
    if len(hidden) > 1:
        press += [(hidden[1][0] / FPS * 1000, 1), (hidden[1][1] / FPS * 1000, 0)]
    spans = [(a * 1000, b * 1000, f'{b - a:.2f} s', 1) for a, b in zip([t for t, _ in ev], [t for t, _ in ev][1:])]
    im = timing([('손가락\n버튼 위', press, RED), ('LD2 PA5\n측정', led, NAVY), ('LD2 PA5\n계산', cpts, GREEN)],
                0, end * 1000, 1, spans,
                notes=['1.27~2.20 s는 손가락이 LED를 가림. 그 사이의 꺼짐은 가려진 시작에 그림',
                       '계산: 간격 1 s, 첫 누름 뒤 2 s, 두 번째 누름 뒤 4 s (코어 정지 없음)'])
    im.save(IMG / 'meas' / 'stm_task3_timing.png')
    print(IMG / 'meas' / 'stm_task3_timing.png')
    return ev, hidden, c


# ------------------------------------------------------------ ADC·PWM 읽은 값
def manual_tables():
    rows = []
    for t, ch, on, what in ADC_READ:
        b = led_bits(on)
        rows.append((t, ch, b, int(b, 2), what))
    write_csv('adc_led_readout.csv', '# t_s,channel,LED1..LED8,led_value,action  (장면을 보고 읽은 값)', rows)
    write_csv('pwm_duty_readout.csv', '# t_s,ch1_positive_duty_percent  (오실로스코프 측정 표시를 읽은 값)', PWM_READ)


def main():
    meas = piano()
    board_piano(meas)
    board_traffic()
    board_adc()
    board_task3()
    board_task4()
    manual_tables()
    print('traffic', traffic())
    print('task3', task3())


if __name__ == '__main__':
    main()
