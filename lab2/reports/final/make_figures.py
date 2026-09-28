"""LAB2 결과보고서용 그림 생성: 원본 캡처에서 파형 영역만 잘라 figures/에 저장한다."""
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
LAB2 = HERE.parents[1]
VIV = HERE / 'images' / 'vivado'
VSC = LAB2 / 'images'
BOARD = HERE / 'images'
OUT = HERE / 'figures'

# (파일, 파형 영역 비율 좌표 x0, y0, x1, y1)
VIVADO = {
    '01': ('SCR-20260928-bhiw.png', 0.347, 0.140, 1.0, 0.660),
    '02': ('SCR-20260928-bdqj.png', 0.349, 0.150, 1.0, 0.600),
    '03': ('SCR-20260928-biwc.png', 0.350, 0.140, 1.0, 0.845),
    '04': ('SCR-20260928-bjsg.png', 0.348, 0.140, 1.0, 0.615),
    '05': ('SCR-20260928-blfu.png', 0.347, 0.140, 1.0, 0.910),
    '06': ('SCR-20260928-bmlo.png', 0.347, 0.140, 1.0, 0.570),
    '07': ('SCR-20260928-bnni.png', 0.346, 0.250, 1.0, 0.960),
    '08': ('SCR-20260928-bovi.png', 0.346, 0.235, 1.0, 0.962),
}
# (파일, 파형 영역, PASS 로그 영역) — 비율 좌표
VSCODE = {
    '01': ('스크린샷 2026-09-20 22.49.39.png', (0.0, 0.110, 1.0, 0.345), (0.0, 0.790, 1.0, 0.885)),
    '02': ('스크린샷 2026-09-20 23.49.40.png', (0.268, 0.110, 1.0, 0.385), (0.268, 0.825, 1.0, 0.900)),
    '03': ('스크린샷 2026-09-20 23.50.44.png', (0.265, 0.105, 1.0, 0.300), (0.265, 0.825, 1.0, 0.900)),
    '04': ('스크린샷 2026-09-20 23.52.14.png', (0.263, 0.110, 1.0, 0.305), (0.263, 0.820, 1.0, 0.900)),
    '05': ('스크린샷 2026-09-20 23.53.09.png', (0.212, 0.108, 1.0, 0.320), (0.212, 0.810, 1.0, 0.880)),
    '06': ('스크린샷 2026-09-20 23.53.47.png', (0.240, 0.100, 1.0, 0.285), (0.240, 0.840, 1.0, 0.905)),
    '07': ('스크린샷 2026-09-20 23.54.33.png', (0.275, 0.105, 1.0, 0.315), (0.275, 0.815, 1.0, 0.880)),
    '08': ('스크린샷 2026-09-20 23.55.30.png', (0.272, 0.105, 1.0, 0.255), (0.272, 0.862, 1.0, 0.940)),
}
BOARD_PHOTOS = {
    'a': ('SCR-20260927-uolq.jpeg', (0.25, 0.26, 0.95, 0.78)),
    'b': ('스크린샷 2026-09-27 23.52.16.png', (0.08, 0.20, 0.82, 0.70)),
    'c': ('스크린샷 2026-09-27 23.52.23.png', (0.08, 0.22, 0.82, 0.72)),
    'd': ('스크린샷 2026-09-27 23.52.27.png', (0.06, 0.20, 0.82, 0.74)),
}


def crop(im, box):
    w, h = im.size
    x0, y0, x1, y1 = box
    return im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))


def stack(parts, gap=6, color=(128, 128, 128)):
    width = max(p.width for p in parts)
    height = sum(p.height for p in parts) + gap * (len(parts) - 1)
    out = Image.new('RGB', (width, height), color)
    y = 0
    for p in parts:
        out.paste(p, (0, y))
        y += p.height + gap
    return out


def main():
    OUT.mkdir(exist_ok=True)
    for lab, (name, *box) in VIVADO.items():
        crop(Image.open(VIV / name).convert('RGB'), box).save(OUT / f'viv_{lab}.png')
    for lab, (name, wave, log) in VSCODE.items():
        im = Image.open(VSC / name).convert('RGB')
        stack([crop(im, wave), crop(im, log)]).save(OUT / f'vsc_{lab}.png')
    for key, (name, box) in BOARD_PHOTOS.items():
        img = crop(Image.open(BOARD / name).convert('RGB'), box)
        img.thumbnail((1400, 1400))
        img.save(OUT / f'board_{key}.jpg', quality=90)
    # Lab 2.08 Vivado 파형의 첫 bank 한 바퀴(0–330 ns)를 신호 이름과 붙여 확대
    im = Image.open(VIV / VIVADO['08'][0]).convert('RGB')
    rows = (0.235, 0.745)
    names = crop(im, (0.346, rows[0], 0.505, rows[1]))
    wave = crop(im, (0.578, rows[0], 0.722, rows[1]))
    zoom = Image.new('RGB', (names.width + wave.width + 4, names.height), (128, 128, 128))
    zoom.paste(names, (0, 0))
    zoom.paste(wave, (names.width + 4, 0))
    zoom.save(OUT / 'viv_08_zoom.png')

if __name__ == '__main__':
    main()
