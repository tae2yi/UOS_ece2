# LAB5 (10/19) — STM32_1 + FPGA 피아노·신호등·ADC — 완료

## 범위
- STM32_1: **과제3** STM32_0 과제1을 버튼 ISR + TIM6 ISR로 재현, **과제4** 버튼으로 PWM 듀티 50→75→25→… (PB4, 1 kHz). 호스트 시뮬레이션 `lab5/stm32_1_hostsim/`(`variants/release_guard.c`).
- FPGA: `lab5_01_piano`(키패드 8개 → 피에조 도~높은 도, `note_select.v`, `square_tone.v`), `lab5_02_traffic`(4방향 신호등 FSM, 신호등 모듈 EXT41~64, flicker SW2),
  `lab5_03_adc`(AD7908 SPI, DIP1~3 채널 선택, LED에 8비트 값).

## 산출물
- 예비 `lab5/report/pre/LAB5_예비보고서.docx`(`57136f0` → XDC·bitstream 추가 `a953f24` → 링크 고정 `9129133`). 조교 매뉴얼을 참고문헌에서 빼라는 지시가 이때 나옴.
- 실습 당일(10/19) 사용자가 신호등 핀·ADC 확인법·DIP_SW1 위치를 실시간 질문 → 교재 사진으로 핀 확인, ADC 수정 bitstream `adc_board_fix.bit` 즉석 제작(`59d5b5f`).
- 결과 `lab5/report/final/LAB5_결과보고서.docx`(8쪽): 영상·측정 `4ff988d`, 보고서 `2ca573d`, 참고문헌 [5] 예비보고서 제거 `19f7d9b`. 참고문헌 [1] Yiu, [2] Mano, [3] STM32CubeG4, [4] AD7908 데이터시트.

## 결과에서 나온 것
- 피아노: 영상 음성으로 8음 주파수, 설계값과 0.11 Hz 이내. 신호등: 보행 초록 17번 변화 시각이 모두 계산과 같은 프레임. 과제4: 듀티 50→75→25→50→75 %, 1 kHz 유지.
- 과제3: 1→2→4 s 규칙은 맞으나 두 번째 누름 뒤 1.47 s 지연(디버그 모드 정지로 설명), 첫 누름 뒤 0.10 s 지연은 원인 미정으로 기록.
- **ADC 이야기**:
  1. 원본 설계에서 DIP1을 바꿔도 채널이 안 바뀜 → 조교 설계가 SCLK 하강 에지(칩이 DIN을 읽는 순간)에 DIN을 바꿈. 수정본: DIN을 상승 에지에 바꾸고, CS HIGH를 40 ns → 0.5 µs 이상. `board_fix/`(`serial_frame16.v`, `tb_fix.sv`, `build_fix.tcl`), 원본 보존.
  2. 수정본에서 채널 전환은 됐지만 LED8이 한 번도 안 켜지고 최대 1111_1110 → FPGA가 DOUT을 1비트 늦게 받음(칩은 CS 하강 때 첫 비트를 냄) → 값이 2배로 보이고 MSB 소실. `board_fix/tb_dout.sv`로 재현. 개선안 LED에 `rx_word[12:5]`. 보드 미검증 → "원인 추정".
- CdS는 가렸을 때 끝까지(0/255) 안 가도 됨. 위쪽 LED(1~4) 패턴이 바뀌어 유지되는지가 기준(LED7·8 깜빡임은 잡음).
