"""LAB7 결과보고서 그림·측정값 생성기.

videos/의 영상(과제 9~12)과 original/의 오실로스코프 사진(과제 8)에서
- images/scope/*.jpg : 오실로스코프 화면 사진(과제 8)
- images/board/*.jpg : 보드·화면 사진(영상 장면에 시각과 값을 적은 것)
- data/*.csv         : 사진·영상에서 읽은 측정값
을 만든다. 오실로스코프의 시간 간격은 화면 사진의 화소 위치로 읽었고, SCK 상승 에지 간격(786.2 kHz)을 자로 썼다.
시리얼 모니터 글자와 보드 LED 값은 장면을 보고 사람이 읽은 값이라 아래 표(SCOPE_READ 등)에 적어 둔다.

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
from make_figures import BLACK, NAVY, font  # noqa: E402

VID = HERE / 'videos'
ORIG = VID / 'original'
IMG = HERE / 'images'
DATA = HERE / 'data'
FFMPEG = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
FPS = 30

SCOPE1 = ORIG / 'KakaoTalk_20261103_193729313.jpg'      # CH1 MOSI, CH2 SCK
SCOPE2 = ORIG / 'KakaoTalk_20261103_193729313_01.jpg'   # CH1 CS, CH2 SCK
SETUP = ORIG / 'KakaoTalk_20261103_193729313_04.jpg'    # 과제 8 측정 장면
TASK9 = VID / 'lab7_stm32_01_task9_mcu_to_mcu.mp4'
TASK10 = VID / 'lab7_fpga_01_task10_mcu_to_fpga.mp4'
TASK11 = VID / 'lab7_fpga_02_task11_fpga_to_mcu.mp4'
TASK12 = VID / 'lab7_fpga_03_task12_fpga_to_fpga.mp4'

# 과제 8: 오실로스코프 화면에서 읽은 값. (항목, 값, 읽은 방법)
SCOPE_READ = [
    ('SCK 주파수', '786.2 kHz', 'CH2 자동 측정(사진 1)'),
    ('MOSI 주파수 (0x55)', '391.2 kHz', 'CH1 자동 측정(사진 1)'),
    ('신호 최대 / 피크-피크', '3.64 V / 3.92 V', 'CH1 자동 측정(사진 1)'),
    ('SCK 펄스 수', '8', '사진 2에서 셈'),
    ('CS LOW -> 첫 SCK 상승', '약 3.0 us', '사진 2 화소, SCK 주기를 자로 사용'),
    ('마지막 SCK 하강 -> CS HIGH', '약 3.4 us', '사진 2 화소'),
    ('CS LOW 전체', '약 15.8 us', '사진 2 화소'),
]
# 시리얼 모니터에서 읽은 줄(위에서 아래로). (영상, 시각 s, 줄)
SERIAL_READ = [
    ('task9', 5.5, 'RX=00 RX=FF RX=55 RX=A5 RX=00'),
    ('task11', 2.5, 'RX=00 RX=FF RX=55 RX=A5 RX=00 RX=FF RX=55 RX=A5 RX=00 RX=FF RX=55 RX=A5 RX=00 RX=FF RX=55'),
]
# 과제 12: 두 보드의 LED1~8(장면을 보고 읽음). 영상에서 위쪽이 송신 보드다. (시각 s, 송신, 수신)
TASK12_READ = [(6.0, 'A5', 'A5'), (6.5, '00', '00'), (7.0, '00', '00'), (7.5, 'FF', 'FF'),
               (8.0, 'FF', 'FF'), (8.5, '55', '55'), (9.0, '55', '55')]


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
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(int)


def write_csv(name, header, rows):
    DATA.mkdir(exist_ok=True)
    (DATA / name).write_text(header + '\n' + '\n'.join(','.join(str(x) for x in r) for r in rows) + '\n',
                             encoding='utf-8')
    print(DATA / name)


def fit(im, width):
    return im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)


def crop(video, t, box, width, rotate=0):
    im = grab(video, t).crop(box)
    if rotate:
        im = im.rotate(rotate, expand=True)
    return fit(im, width)


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


# ------------------------------------------------------------ 과제 8: 오실로스코프
def scope():
    a = fit(Image.open(SCOPE1).convert('RGB').crop((135, 380, 3900, 2555)), 1000)
    b = fit(Image.open(SCOPE2).convert('RGB').crop((715, 740, 3990, 2375)), 1000)
    sheet([(a, '사진 1  CH1 MOSI (노랑), CH2 SCK (파랑), 4 us/div',
            '0x55 = 0101_0101, SCK 786.2 kHz, MOSI 391.2 kHz')], 1, 1000,
          IMG / 'scope' / 'scope_sck_mosi.jpg', sizes=(24, 22))
    sheet([(b, '사진 2  CH1 CS (노랑), CH2 SCK (파랑), 4 us/div',
            'CS LOW 동안 SCK 8펄스, CS 상승 에지 트리거')], 1, 1000,
          IMG / 'scope' / 'scope_cs_sck.jpg', sizes=(24, 22))
    s = fit(Image.open(SETUP).convert('RGB'), 1000)
    sheet([(s, '과제 8 측정 장면', 'NUCLEO-G474RE 혼자, 프로브 2개를 SCK·MOSI(또는 CS)에 연결')], 1, 1000,
          IMG / 'board' / 'stm_task8_setup.jpg', sizes=(24, 22))
    write_csv('task8_scope_readout.csv', '# item,value,method  (오실로스코프 사진에서 읽은 값)', SCOPE_READ)


# ------------------------------------------------------------ 과제 9: MCU -> MCU
def board_task9():
    a = crop(TASK9, 0.3, (0, 0, 1440, 1080), 480)
    b = crop(TASK9, 5.5, (150, 200, 1050, 700), 520)
    sheet([(a, '0.3 s  NUCLEO 두 대', '송신(ROLE=1) -> 수신(ROLE=2), GND 공통'),
           (b, '5.5 s  수신 보드 직렬 모니터', 'RX=00, FF, 55, A5, 00 차례로 수신')], 2, 520,
          IMG / 'board' / 'stm_task9.jpg', sizes=(21, 19))


# ------------------------------------------------------------ 과제 10: MCU -> FPGA, LED
T10_BOX = (300, 420, 1000, 680)
T10_LEDS = [126, 186, 246, 306]      # LED1~4의 x (T10_BOX 안, y 70~115). 오른쪽 LED는 손떨림으로 상자 밖에 나가 쓰지 않는다


def task10():
    x0, y0, x1, y1 = T10_BOX
    rows, prev, edges = [], None, []
    for i, f in enumerate(frames(TASK10, 1440, 1080)):
        f = f[y0:y1, x0:x1]
        r = f[..., 0] - (f[..., 1] + f[..., 2]) // 2
        bits = ''.join('1' if (r[70:115, x - 18:x + 18] > 120).sum() > 40 else '0' for x in T10_LEDS)
        t = i / FPS
        rows.append((f'{t:.3f}', bits))
        if prev is not None and bits != prev and t < 2.5:
            edges.append((round(t, 3), prev, bits))
        prev = bits
    write_csv('task10_led1_4.csv', '# t_s,LED1..LED4  (프레임마다 LED 위치의 빨간 화소로 판정)', rows)
    shots = [(0.1, 'FF', 'LED1~8 모두 켜짐'), (0.6, '55', '0101_0101'),
             (1.6, 'A5', '1010_0101'), (2.4, '00', 'LED1~8 모두 꺼짐')]
    sheet([(crop(TASK10, t, T10_BOX, 496), f'{t:.1f} s  값 {v}', b) for t, v, b in shots], 2, 496,
          IMG / 'board' / 'fpga_task10.jpg')
    return edges


# ------------------------------------------------------------ 과제 11: FPGA -> MCU
def board_task11():
    a = crop(TASK11, 2.5, (300, 380, 1000, 860), 480)
    b = crop(TASK11, 10.5, (0, 300, 1440, 1080), 480)
    sheet([(a, '2.5 s  MCU 직렬 모니터', 'RX=00, FF, 55, A5 반복'),
           (b, '10.5 s  FPGA 송신 보드', 'LED에 보내는 값, BDIO_0~2 -> D3·D11·A2')], 2, 480,
          IMG / 'board' / 'fpga_task11.jpg', sizes=(21, 19))


# ------------------------------------------------------------ 과제 12: FPGA -> FPGA
def board_task12():
    tiles = []
    for t, up, down in TASK12_READ[::2]:
        a = crop(TASK12, t, (540, 110, 660, 310), 330, rotate=90)
        b = crop(TASK12, t, (200, 1080, 560, 1200), 330)
        both = Image.new('RGB', (330, a.height + b.height + 6), 'white')
        both.paste(a, (0, 0))
        both.paste(b, (0, a.height + 6))
        tiles.append((both, f'{t:.1f} s', f'송신 {up}, 수신 {down}'))
    sheet(tiles, 4, 330, IMG / 'board' / 'fpga_task12.jpg', sizes=(21, 19))
    full = crop(TASK12, 6.0, (0, 0, 1080, 1440), 600)
    sheet([(full, '6.0 s  FPGA 두 대', '위 송신, 아래 수신. BDIO_0~2와 GND 연결')], 1, 600,
          IMG / 'board' / 'fpga_task12_boards.jpg', sizes=(22, 20))
    write_csv('task12_led_readout.csv', '# t_s,tx_board_hex(위쪽),rx_board_hex(아래쪽)  (장면을 보고 읽은 값)',
              TASK12_READ)


def main():
    scope()
    board_task9()
    print('task10 edges', task10())
    board_task11()
    board_task12()
    write_csv('serial_readout.csv', '# video,t_s,lines  (직렬 모니터 화면을 보고 읽은 줄)', SERIAL_READ)


if __name__ == '__main__':
    main()
