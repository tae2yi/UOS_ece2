# 수정실험 기록 — 4비트 카운터

## 교안 지시

교안 `../pdf/05.LAB2_01_COUNTER_VIVADO.pdf` 35–40쪽은 정상실험 파형을 열고 `clk`, `rst`, `enable`, `down`, `value[3:0]`를 관찰한 뒤 결과를 보고서에 넣도록 안내한다. 76쪽 전체에서 별도의 `수정 실험`/`수정실험` 항목이나 수정할 RTL을 제시하지 않는다. 따라서 교안에 없는 고장 주입은 만들지 않았고 RTL·TB는 수정하지 않았다.

## 기대 동작과 결과

정상 TB는 리셋, 4비트 증가·감소, 양방향 랩어라운드, enable 유지, 리셋 우선순위를 검사한다. 보관된 정상 실행은 `LAB2_PASS counter4 checks=36`으로 끝난다.

| 항목 | 기록 |
|---|---|
| 수정한 파일·신호 | 없음. 정상 RTL과 `sim/tb_counter4.sv` 유지 |
| 정상 파형 신호 | `clk`, `rst`, `enable`, `down`, `value[3:0]` |
| 정상 캡처 | `evidence/normal/normal_screenshot.png` — `lab2/images`의 2026-09-20 22:49:39 캡처를 파일명 순서로 연결 |
| 로그·파형 | 현재 캡처 실행은 `evidence/normal/current_normal_simulation.log`, `evidence/normal/current_normal_wave.vcd`; 재현용 입력은 `evidence/normal/source/` |
| 기존 자료 | 기존 `evidence/normal/wave.vcd` 및 `counter4_normal_waveform.png`는 덮어쓰지 않고 보존 |

교안이 별도 수정실험을 요구하지 않으므로 수정 파형과 수정 로그는 없다. 보관된 스크린샷은 VaporView의 정상 파형과 `checks=36` PASS를 함께 보여 준다.
