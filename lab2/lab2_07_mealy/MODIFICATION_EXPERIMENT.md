# 수정 실험 — Mealy 입력 1의 출력 교환

## 교안 지시와 출처

출처: [`05.LAB2_07_MEALY_VIVADO.pdf`](../pdf/05.LAB2_07_MEALY_VIVADO.pdf), 수정 실험 인쇄 쪽수 41, 파형 해설 쪽수 43. 두 페이지를 렌더링해 지시와 기대 결과를 시각적으로 확인했다.

교안은 정상 로그와 파형을 먼저 보관하고, 입력 1일 때 두 상태의 출력을 서로 바꾸되 TB 기대값은 유지하도록 한다. `02 Simulate`에서 검사명과 시각을 확인하고 입력 및 이전 상태를 계산한 뒤 RTL을 복구해 전체 PASS를 확인한다. 해설은 7 ns의 `S0 input changes between clocks` 검사에서 기대 `{state,value}=010`, 변경값 `001`로 실패하며, 원복 후 11개 PASS와 67 ns 종료를 확인하라고 명시한다.

## 변경과 예상 동작

- 변경 RTL: [`src/mealy_toggle.v`](src/mealy_toggle.v)의 조합 출력에서 입력 1일 때 S0/S1의 출력 `10`과 `01`을 서로 바꿨다.
- 테스트벤치: [`sim/tb_mealy_toggle.sv`](sim/tb_mealy_toggle.sv)는 바꾸지 않았다. S0에서 입력 1이면 `{state,value}=010`이어야 한다.
- 관찰 신호: `clk`, `rst`, `enable`, `bit_in`, `state`, `value[1:0]`.
- 예상 실패: 첫 클록 리셋 후 `state=0`(S0), `bit_in=1`, `enable=0`에서 조합 출력이 클록 사이에 바뀐다. 원래 출력은 `10`이지만 변경 회로는 `01`을 내므로 7 ns 검사에서 `{state,value}`가 `001`이 되어 실패한다.

## 실행 결과

| 상태 | 결과 |
|---|---|
| 정상 기준 | `LAB2_PASS mealy_toggle checks=11`, 종료 67 ns |
| 입력 1 출력을 교환한 RTL | `LAB2_FAIL S0 input changes between clocks time=7000` (7 ns); 기대 `010`, 실제 `001` |
| RTL 원복 | `LAB2_PASS mealy_toggle checks=11`, 종료 67 ns |

Icarus 비 GUI 시뮬레이션으로 실행했다. 수정 RTL 실행은 TB의 `$fatal`로 의도한 첫 불일치에서 종료 코드 1을 반환한다. 실패 시점까지의 VCD와 로그를 별도 보관했다. RTL을 정상 원본으로 복구한 뒤 11개 검사가 모두 통과했다.

## 캡처와 재현 자료

- 정상 원본 스냅샷: [`evidence/normal/source/`](evidence/normal/source/) — RTL, TB, 설정, 제약.
- 정상 로그와 파형: [`evidence/normal/simulation.log`](evidence/normal/simulation.log), [`evidence/normal/wave.vcd`](evidence/normal/wave.vcd).
- 정상 스크린샷: [`evidence/normal/normal_screenshot.png`](evidence/normal/normal_screenshot.png). `lab2/images` 시간순 7번째 파일(2026-09-20 23:54:33)을 복사했다.
- 수정 RTL 스냅샷: [`evidence/modified/source/mealy_toggle.v`](evidence/modified/source/mealy_toggle.v). TB는 정상 원본 스냅샷과 동일하다.
- 수정 로그, VCD, 보고서용 파형: [`evidence/modified/simulation.log`](evidence/modified/simulation.log), [`evidence/modified/wave.vcd`](evidence/modified/wave.vcd), [`evidence/modified/waveform.png`](evidence/modified/waveform.png).
- 복구 로그와 파형: [`evidence/recovered/simulation.log`](evidence/recovered/simulation.log), [`evidence/recovered/wave.vcd`](evidence/recovered/wave.vcd).

파형에는 S0에서 `bit_in=1`이 된 직후 바뀐 출력 `01`과 7 ns 실패 경계가 보인다. 교안의 값과 실행 로그가 일치하며 해석상 불확실성은 없다. 작업 트리 RTL은 원복 상태다.
