"""영상에 비친 얼굴을 모자이크하고 H.264로 다시 인코딩한다.

과제 9·11 영상은 노트북 화면에 촬영자와 옆 사람의 얼굴이 비친다. 얼굴 위치를 프레임에서 보고 시각별 상자로 적었고
(아래 TASK9·TASK11, 1440x1080 화소 좌표), 상자 사이 시각은 선형 보간한다. 과제 10·12 영상에는 얼굴이 없어 그대로 인코딩한다.
원본은 videos/original/에 있고 결과는 videos/<이름>.mp4를 덮어쓴다. 이 영상에서 make_figures.py가 보고서 사진을 뽑는다.

실행: python blur_faces.py [ffmpeg 경로]   (numpy 필요)
"""
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
VID = HERE / 'videos'
ORIG = VID / 'original'
FFMPEG = sys.argv[1] if len(sys.argv) > 1 else 'ffmpeg'
FPS = 30
BLOCK = 28          # 모자이크 한 칸(화소)

# (시작 s, 끝 s, 시작 상자, 끝 상자). 상자 = (x0, y0, x1, y1)
TASK9 = [
    (1.40, 2.10, (450, 330, 1120, 680), (450, 330, 1120, 680)),    # 화면 가운데에 작게 비친 촬영자
    (2.10, 2.40, (200, 380, 1120, 860), (200, 380, 1120, 860)),    # 촬영자에서 옆 사람으로 넘어가는 구간
    (2.40, 2.50, (90, 480, 450, 880), (90, 500, 440, 880)),
    (2.50, 2.75, (90, 500, 440, 880), (40, 480, 420, 880)),
    (2.75, 3.00, (40, 480, 420, 880), (40, 450, 430, 780)),
    (3.00, 3.50, (40, 450, 430, 780), (60, 420, 450, 760)),
    (3.50, 4.00, (60, 420, 450, 760), (40, 360, 480, 700)),
    (4.00, 4.50, (40, 360, 480, 700), (40, 360, 470, 700)),
    (4.50, 5.00, (40, 360, 470, 700), (40, 400, 470, 740)),
    (5.00, 5.50, (40, 400, 470, 740), (60, 400, 500, 760)),
    (5.50, 6.00, (60, 400, 500, 760), (80, 340, 540, 700)),
    (6.00, 6.20, (80, 300, 1040, 700), (80, 300, 1040, 700)),
    (6.20, 6.40, (740, 300, 1060, 620), (740, 300, 1060, 620)),
    (6.40, 6.65, (800, 180, 1120, 440), (800, 180, 1120, 440)),
    (6.65, 6.95, (780, 60, 1140, 360), (780, 60, 1140, 360)),
]
TASK11 = [
    (0.00, 3.60, (800, 0, 1440, 700), (800, 0, 1440, 700)),        # 직렬 모니터 글자 오른쪽에 비친 촬영자
    (0.00, 3.60, (0, 0, 1440, 400), (0, 0, 1440, 400)),            # 글자 위쪽에 비친 머리
    (3.60, 3.90, (0, 0, 1440, 560), (0, 0, 1440, 560)),
    (3.90, 4.90, (0, 0, 1440, 900), (0, 0, 1440, 900)),        # 두 사람이 크게 비침
]

JOBS = [  # (원본, 결과, 얼굴 상자)
    ('KakaoTalk_20261103_193736135.mp4', 'lab7_stm32_01_task9_mcu_to_mcu.mp4', TASK9),
    ('KakaoTalk_20261103_193744000.mp4', 'lab7_fpga_01_task10_mcu_to_fpga.mp4', []),
    ('KakaoTalk_20261103_193756626.mp4', 'lab7_fpga_02_task11_fpga_to_mcu.mp4', TASK11),
    ('KakaoTalk_20261103_193738588.mp4', 'lab7_fpga_03_task12_fpga_to_fpga.mp4', []),
]


def size(video):
    """회전 정보가 적용된 뒤의 (폭, 높이). 세로 영상은 디코딩하면 세로가 된다."""
    png = subprocess.run([FFMPEG, '-loglevel', 'error', '-i', str(video), '-frames:v', '1',
                          '-f', 'image2pipe', '-vcodec', 'png', '-'], stdout=subprocess.PIPE, check=True).stdout
    return Image.open(io.BytesIO(png)).size


def boxes_at(faces, t):
    out = []
    for t0, t1, a, b in faces:
        if t0 <= t < t1:
            k = (t - t0) / (t1 - t0)
            out.append(tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(4)))
    return out


def pixelate(f, box):
    h, w, _ = f.shape
    x0, y0, x1, y1 = max(0, box[0]), max(0, box[1]), min(w, box[2]), min(h, box[3])
    for y in range(y0, y1, BLOCK):
        for x in range(x0, x1, BLOCK):
            cell = f[y:min(y + BLOCK, y1), x:min(x + BLOCK, x1)]
            cell[:] = cell.reshape(-1, 3).mean(0)


def run(src, dst, faces):
    w, h = size(src)
    dec = subprocess.Popen([FFMPEG, '-loglevel', 'error', '-i', str(src), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen([FFMPEG, '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-', '-i', str(src),
                            '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
                            '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-c:a', 'aac', '-b:a', '128k',
                            '-shortest', str(dst)], stdin=subprocess.PIPE)
    i = n = 0
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(h, w, 3).copy()
        boxes = boxes_at(faces, i / FPS)
        for box in boxes:
            pixelate(f, box)
        n += bool(boxes)
        enc.stdin.write(f.tobytes())
        i += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(f'{dst.name}: {i} frames, {n} mosaicked')


def main():
    for src, dst, faces in JOBS:
        run(ORIG / src, VID / dst, faces)
        thumb = VID / 'thumb' / (Path(dst).stem + '.jpg')
        subprocess.run([FFMPEG, '-loglevel', 'error', '-y', '-ss', '1', '-i', str(VID / dst), '-frames:v', '1',
                        '-vf', 'scale=320:-1', '-q:v', '3', str(thumb)], check=True)


if __name__ == '__main__':
    main()
