# LAB7 (11/2) — STM32_3 SPI (과제8~12) — 예비·결과 완료

## 범위 (조교 `c/stm32/docs/STM32_3.md`, 저장소 Glaysia/ece2_26_2_2 커밋 1fab83e)
- SPI Mode 0, 8비트, MSB first, MISO 미사용. MCU SPI1 SCK = 100 MHz / 128 = 781.25 kHz. FPGA 마스터는 1 MHz 이하.
- MCU 핀: SCK PB3, MOSI PA7, 송신 CS PB6(GPIO), 수신 NSS PA4(AF5). 수신 측은 `ece2_474_init()`에서 SPI1을 슬레이브·NSS 하드 입력으로 재설정.
- 과제8 MCU 송신 파형 / 과제9 MCU→MCU(옆 조, A–B…) / 과제10 MCU→FPGA / 과제11 FPGA→MCU / 과제12 FPGA→FPGA(옆 조). FPGA Verilog 정답은 없음 → 직접 설계.
- 이번 주 FPGA 교재 실습 없음, I²C 안 함.

## 코드
- MCU: `lab7/stm32_lab/Core/Src/ece2_474_routine.c`
  - `STM32_3_ROLE=1`(기본, 송신: 0x55→0xA5→0x00→0xFF를 1초마다) / `=2`(수신). 한 값만: `-DSTM32_3_TX_FIXED=0x55`.
  - 매뉴얼 한 줄(RX timeout printf)을 63자 폭 때문에 문자열 두 개로 나눔(동작 동일).
- 호스트 시뮬레이션 `lab7/stm32_3_hostsim/`: `master <초> out.hex wave.csv` / `slave in.hex`("--" 줄 = 2초 무응답). `run_hostsim.sh`.
- FPGA (핀 공통: SCK=BDIO_0 F8, MOSI=BDIO_1 E8, CS_n=BDIO_2 A7, UART TX F6, LED1=bit7…LED8=bit0, DIP SW5 ON)
  - `lab7_01_spi_rx` (top `spi_rx_uart`): 2단 동기화 + 상승 에지 검출 + 시프트, CS HIGH면 카운터 0. 받은 값을 "RX=55\r\n"으로 UART, LED. 입력 풀다운(SCK·MOSI)/풀업(CS). WNS +14.349 ns, bitstream 있음.
  - `lab7_02_spi_tx` (top `spi_tx_uart`): 1초마다 55·A5·00·FF, SCK 500 kHz(HALF=50), CS LOW 17 µs, "TX=55\r\n" UART, LED. WNS +15.484 ns, bitstream 있음.
  - `lab7_03_spi_link`: 과제12 시뮬레이션 전용(src는 01·02의 사본, `run_icarus.sh`가 매번 복사). 두 보드 클록 20.000/20.050 ns, 선 지연.
- 검증 흐름(`report/pre/tools/run_icarus.sh`): hostsim master → `lab7_01/sim/mcu_spi.hex` → FPGA TB, `lab7_02` TB → `sim/fpga_tx_bytes.hex` → hostsim slave. Icarus·xsim 6개씩 PASS.
- 캡처: 긴 tb(약 90 ms)는 xsim GUI가 0~700 ms로 열어 파형이 몰림 → `capture_xsim.ps1 -Keys "^0"`(Zoom Fit)로 찍음. wcfg zoom_setting 수정은 효과 없었음.

## 산출물
- `lab7/report/pre/LAB7_예비보고서.docx` (11쪽), `qa_render/LAB7_예비보고서.pdf`. 링크는 커밋 `19a037b`로 고정(`8cdd3cc`).

## 실험 당일 확인할 것
1. 받는 쪽에 수신 프로그램/bitstream을 **먼저** 올리고 선 연결(출력끼리 충돌 방지). 과제11 전 MCU를 `-DSTM32_3_ROLE=2`로.
2. 과제9 역할 교대 때 CS 선을 새 송신 PB6 → 새 수신 PA4로 옮김.
3. 오실로스코프: MCU SCK 1.28 µs, CS↓→첫 SCK↑ 시간(HAL 처리 시간, 예비에서 미정), FPGA SCK 2 µs·CS 17 µs.
4. 수신 MCU가 송신 도중 시작하면 값이 밀릴 수 있음(추정) → 수신 리셋 후 다시.

## 결과보고서 (11/3, `lab7/report/final/`)
- 자료: 오실로스코프 사진 2장(과제8, 사진1 CH1 MOSI·CH2 SCK, 사진2 CH1 CS·CH2 SCK), 장면 사진 3장, 영상 4개(과제9 MCU→MCU, 10 MCU→FPGA, 11 FPGA→MCU, 12 FPGA→FPGA). 원본은 `videos/original/`(gitignore).
- 측정: SCK 786.2 kHz(+0.6 %), MOSI 391.2 kHz(0x55), CS→첫 SCK 약 3.0 µs, 마지막 SCK→CS 약 3.4 µs, CS LOW 약 15.8 µs(사진 화소, SCK 주기를 자로). 과제10 LED 바뀐 시각 0.20·1.17·2.17 s.
- 과제12 영상은 **위쪽 보드가 송신**(사용자 확인). 과제9 역할 교대는 **보고서에 쓰지 않음**(사용자 요청).
- 얼굴: 과제9·11 영상은 노트북 화면에 비친 얼굴이 있어 `blur_faces.py`(시각별 상자, 수동)로 모자이크 후 인코딩. make_figures는 모자이크된 영상에서 사진을 뽑는다.
- 순서: `blur_faces.py <ffmpeg>` → `make_figures.py <ffmpeg>` → `build_lab7_final.py`.
