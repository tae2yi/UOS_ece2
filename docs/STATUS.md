# 현재 상태와 다음 할 일

기준: **2026-10-21(수)**. 작업이 끝날 때마다 이 파일을 갱신한다.

## 진행 현황

| LAB | 날짜 | 내용 | 예비보고서 | 결과보고서 |
|---|---|---|---|---|
| LAB1 | 9/14 | FPGA 조합회로 10개 | 완료 | 완료(`lab1/report/results`) |
| LAB2 | 9/21 | FPGA 순차회로 8개 | 완료 | 완료 |
| LAB3 | 9/28 | FPGA 주변장치 7개(시연: 07 UART 에코) | 완료 | 완료, 태그 `lab3-final` |
| LAB4 | 10/12 | STM32_0(과제1·2) + FPGA 곱셈기·BCD 변환 | 완료(`570f69c`, 링크 고정 `8c45792`) | **docx·스크립트 미커밋**(아래) |
| LAB5 | 10/19 | STM32_1(과제3·4) + FPGA 피아노·신호등·ADC | 완료(`a953f24`, 고정 `9129133`) | 완료(`2ca573d`, 참고문헌 수정 `19f7d9b`) |
| LAB6 | 10/26 | STM32_2(과제5~7) + FPGA 서보·SRAM·DAC | 완료(`cb8ab23`, 고정 `eefd5c7`) **push 안 됨** | 실험 후 |
| LAB7 | 11/2 | STM32_3(과제8~12, SPI) | 시작 전 | — |

## 걸려 있는 일 (우선순위 순)

1. **LAB6 push 대기** — 로컬 master가 origin보다 2커밋 앞섬(`cb8ab23`, `eefd5c7`). 사용자에게 push 여부를 확인한다. push 해야 보고서 속 링크가 열린다.
2. **LAB6 서보·SRAM 핀 미정** — 장비 교재의 서보 출력 핀, SRAM 버스(주소·데이터·/CS·/OE·/WE, /UB·/LB 연결 여부) 핀 표 사진을 사용자에게 받으면
   `lab6/lab6_01_servo/constraints/servo_board.xdc`(현재 `# set_property PACKAGE_PIN ?? [get_ports servo]`), `lab6/lab6_02_sram/constraints/sram.xdc`를 채우고
   `lab6/report/pre/tools/build_vivado.tcl`에서 두 프로젝트의 bit 플래그를 1로 바꿔 bitstream을 만든다. 서보 타이밍이 깨지면 `lab6_01_servo/variants/servo_pwm_mul.v`(나눗셈 제거판, 여유 +13.5 ns)로 교체.
3. **LAB4 결과보고서 미커밋** — `lab4/report/final/LAB4_결과보고서.docx`, `build_lab4_final.py`, `qa_render/`가 untracked. 보고서에는 제출 태그 `lab4-final`을 적었지만 태그는 만들지 않았다. 사용자가 이미 제출했는지, 커밋·태그를 원하는지 확인 후 처리.
4. **10/26 기획 PPT 진행본 2** — `project/planning/`(untracked). 10/19 진행본을 만든 스크립트 `build_planning_ppt.py`를 고쳐 다시 만든다. 빈칸(조 이름·조장·조원·역할)과 피드백 반영 필요. [project/mini-ate.md](project/mini-ate.md)
5. **LAB6 결과보고서** — 10/26 실험 후. 사용자가 영상을 `lab6/report/final/videos/`에 넣고 요청하면 [workflow/final-report.md](workflow/final-report.md)대로.
6. **LAB7 예비보고서** — STM32_3(SPI, 과제8~12, 11/2). 조교 저장소 `docs/STM32_3.md` 확인부터. MCU–MCU·FPGA–FPGA 과제는 옆 조와 장비 2대가 필요(A–B, C–D … 짝).

## 저장소에 커밋되지 않은 것 (2026-10-21 `git status`)

- `03.LAB0_OT_0907.pdf` (루트, OT 자료 — 원래 올리지 않던 파일이라 그대로 둠)
- `lab4/report/final/LAB4_결과보고서.docx`, `build_lab4_final.py`, `qa_render/`
- `project/` 전체 (기획 PPT)
- `docs/` (이 문서들 — 커밋 여부는 사용자에게 확인), 루트 `.gitignore` 수정(`docs/reference/environment.md` 제외 — 로컬 전용)

## 보드에서 확인되지 않은 설계상 의문점

- **LAB5 ADC**: 수정본 `adc_board_fix.bit`로 채널 전환은 됐지만 LED8이 한 번도 켜지지 않고 최댓값 1111_1110 → FPGA가 DOUT을 1비트 늦게 받는 것으로 추정(`board_fix/tb_dout.sv`로 재현). 고치는 법: LED에 `rx_word[12:5]` 출력. 보드 미검증, 보고서에는 "원인 추정".
- **LAB4 PB0 위치**(CN7-34·A3)는 기억에 의존한 값, UM2505로 확인 못 함.
- **DIP 스위치 방향**(어느 쪽이 1인지) 미확인.
