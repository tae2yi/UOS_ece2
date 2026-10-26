# LAB6 (10/26) — STM32_2 UART + FPGA 서보·SRAM·DAC — 예비 완료, 실험 전

## 범위 (조교 `docs/STM32_2.md`, `docs/FPGA_additional.md` 5·6·8절)
- UART 9600 8N1. PC–MCU UART2(VCP), MCU–FPGA UART3(PC10 TX).
- **과제5** PC → MCU → PC: `'1' 'A' 'a'` → `0x31 0x41 0x61` 출력.
- **과제6** PC → MCU → FPGA → PC: COM 포트 두 개(ST-LINK VCP, FPGA USB-UART)를 열고 FPGA가 받은 문자가 같은지.
- **과제7** PC → MCU → FPGA: `0`=LED 끄기, `1`=켜기, `2`=반전, 그 밖=유지.
- MCU 코드: `lab6/stm32_lab/Core/Src/ece2_474_routine.c`, `STM32_2_TASK=5`(기본) / `6`(과제6·7). 호스트 시뮬레이션 `lab6/stm32_2_hostsim/`.
- FPGA:
  - `lab6_01_servo` — 매뉴얼 `servo_ctrl.zip` 기반(`servo.zip`은 빈 파일). 버튼 떨림 처리 `button_pulse.v` 추가. 50 MHz 타이밍: 핀 미정일 때 +0.023 ns였으나 SERVO = AA22로 확정 후 **−0.848 ns 위반**(펄스 폭 곱셈·나눗셈이 한 클록) → 대비안 `variants/servo_pwm_mul.v`(나눗셈 제거) +13.183 ns. **bitstream 2개**: `servo_board.bit`(매뉴얼, 타이밍 위반) / `servo_board_mul.bit`(대비안, 권장). 매뉴얼 코드 한 줄을 63자 제한 때문에 줄바꿈(동작 동일).
  - `lab6_02_sram` — 클록 없는 제어선 조합, 버스 구동 주체 주의. DIP로 주소·데이터, 버튼 N8 쓰기/N4 읽기, LED 출력. **bitstream 있음**(SRAM 핀 = 교재 p.603).
  - `lab6_03_dac` — 8비트 병렬 DAC(`dac_parallel8.v`, `ramp8.v`), 10 ms마다 쓰기. **bitstream 있음**.
  - `lab6_04_uart_led` — 과제6·7 FPGA 쪽. LAB3 UART 에코 수정, RX = BDIO_0(F8), TX = F6, LED1 = 명령 상태, LED2~8 = 받은 바이트. TB가 `sim/mcu_task6.hex`, `mcu_task7.hex`(호스트 시뮬 결과)를 읽음. **bitstream 있음**.

## 산출물
- `lab6/report/pre/LAB6_예비보고서.docx` (11쪽), 커밋 `cb8ab23`, 링크 고정 `eefd5c7` — **push 안 됨**.
- 검증: 과제5 Arm GCC 빌드 경고 없음, 호스트에서 3개 입력 확인. 과제6·7 호스트 + FPGA TB 연결로 3바이트 에코·명령 9개 LED 일치. 서보·SRAM·DAC TB 2개씩 Icarus·xsim PASS. Vivado 캡처 8장.

## 남은 일
1. (완료) 서보 AA22·SRAM 핀 확정, 4개 설계 bitstream 있음. 대비안 서보 bit는 스크래치 tcl로 따로 만듦(`build_vivado.tcl`은 매뉴얼판만).
2. 실험 당일 확인할 것: PC10 → BDIO_0(F8) + GND, **DIP SW5(BD_SEL) ON**, 클럭 스위치 F(50 MHz), 서보 각도·PWM, DAC 최대 전압(전압계).
3. 실험 후 결과보고서([../workflow/final-report.md](../workflow/final-report.md)). 기록 계획(예비보고서 4장): 과제5 화면, 배선 사진, 두 COM 포트 화면, 과제7 LED 영상, 서보 버튼별 각도·PWM 파형, SRAM LED 값, DAC 전압계 값.
