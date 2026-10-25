# LAB4 (10/12) — STM32_0 + FPGA 곱셈기·BCD 변환

## 범위
- STM32_0: 제공 예제 1(1 s LED 깜빡임)·2(버튼으로 LED 토글), **과제1** 버튼으로 내장 LED(PA5) 간격 1→2→4→8→1 s, **과제2** 같은 동작을 외부 LED(PB0)로(`STM32_0_USE_EXTERNAL_LED` 매크로).
  폴링, `HAL_GetTick` 비교, 에지 검출 + 200 ms lockout, 틱 wrap.
- FPGA: `lab4_01_mult_4bit`(4비트×4비트 조합 곱셈기), `lab4_02_bcd_conv`(BCD→이진). 256개 입력 전수 PASS, DRC 0. 핀은 lab1 스위치·lab3 LED 재사용(교재 핀 표와 대조 안 함).

## 산출물
- 예비: `lab4/report/pre/LAB4_예비보고서.docx` (8쪽, `570f69c`, 링크 고정 `8c45792`). 호스트 시뮬레이션 `lab4/stm32_0_hostsim/`(떨림 대비 `variants/task1_release_guard.c`).
- 맥 실험 매뉴얼 `lab4/manual/LAB4_실험매뉴얼.pdf` (12쪽).
- 결과: `lab4/report/final/` — 영상 4개 `lab4_fpga_01_mult_4bit.mp4, lab4_fpga_02_bcd_conv.mp4, lab4_stm32_01_task1_onboard_led.mp4, lab4_stm32_02_task2_external_led.mp4` + README(`1e93906`, `c8d03b2`).
  **보고서 docx·`build_lab4_final.py`·qa_render는 미커밋, 태그 `lab4-final` 미생성.**

## 결과에서 나온 것
- 곱셈기 LED 0→1→3→7→21→77, BCD 10개 모두 일치. 과제2 간격 1.00, 1.00, 2.00, 2.00, 3.97 s(1프레임 이내).
- 과제1 영상 간격 4.80, 6.83 s → 사용자 설명: **디버그 모드에서 중단점을 함수 안에 걸어 눌 때마다 멈춤**. 정지 2.80·2.83 s를 빼면 규칙과 일치. 근거: 과제1 영상만 ST-LINK LD1이 적·녹 깜빡임. 보고서 6~8장과 README에 반영.
- 영상이 짧아 8초 간격·8→1 순환·길게 누름은 "미확인".
