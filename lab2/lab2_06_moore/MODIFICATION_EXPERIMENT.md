# 수정 실험 — Moore 상태 S1의 다음 상태 변경

## 교안 지시와 출처

출처: [`05.LAB2_06_MOORE_VIVADO.pdf`](../pdf/05.LAB2_06_MOORE_VIVADO.pdf), 수정 실험 인쇄 쪽수 39, 파형 해설 쪽수 41. 두 페이지를 렌더링해 지시와 기대 결과를 시각적으로 확인했다.

교안은 정상 로그와 파형을 먼저 보관한 뒤, S1에서 다음 상태를 S0로 바꾸고 TB 기대값을 유지하도록 한다. 이어 `02 Simulate`에서 `LAB2_FAIL`의 검사 이름과 시각을 확인하고, 불일치 입력과 이전 상태를 계산한 다음 RTL을 복구해 전체 PASS를 확인한다. 해설은 `2'b01`의 다음 상태를 `2'b10`에서 `2'b00`으로 바꿀 때 46 ns의 `S1 to S2` 검사가 실패하고, 원복 후 23개 PASS와 226 ns 종료를 확인하라고 명시한다.

## 변경과 예상 동작

- 변경 RTL: [`src/moore_cycle.v`](src/moore_cycle.v)에서 현재 상태 `2'b01`일 때 다음 `value`를 `2'b10` 대신 `2'b00`으로 설정했다.
- 테스트벤치: [`sim/tb_moore_cycle.sv`](sim/tb_moore_cycle.sv)는 바꾸지 않았다. S1에서 예상하는 다음 상태는 계속 `2'b10`이다.
- 관찰 신호: `clk`, `rst`, `enable`, `advance`, `value[1:0]`.
- 예상 실패: 이전 상태 S1=`01`, `enable=1`, `advance=1`에서 45 ns 상승 에지 후 변경 회로는 S0=`00`으로 돌아간다. TB는 다음 ns인 46 ns에 S2=`10`을 기대하므로 `S1 to S2` 검사에서 실패한다.

## 실행 결과

| 상태 | 결과 |
|---|---|
| 정상 기준 | `LAB2_PASS moore_cycle checks=23`, 종료 226 ns |
| S1 전이를 바꾼 RTL | `LAB2_FAIL S1 to S2 time=46000` (46 ns); 기대 `10`, 실제 `00` |
| RTL 원복 | `LAB2_PASS moore_cycle checks=23`, 종료 226 ns |

Icarus 비 GUI 시뮬레이션으로 실행했다. 수정 RTL 실행은 기대한 첫 불일치에서 TB의 `$fatal`로 종료 코드 1을 반환한다. 그 시점까지의 VCD와 로그를 별도 보관했다. RTL은 정상 스냅샷과 일치하도록 원복했고, 복구 실행은 전체 검사 PASS다.

## 캡처와 재현 자료

- 정상 원본 스냅샷: [`evidence/normal/source/`](evidence/normal/source/) — RTL, TB, 설정, 제약.
- 정상 로그와 파형: [`evidence/normal/simulation.log`](evidence/normal/simulation.log), [`evidence/normal/wave.vcd`](evidence/normal/wave.vcd).
- 정상 스크린샷: [`evidence/normal/normal_screenshot.png`](evidence/normal/normal_screenshot.png). `lab2/images` 시간순 6번째 파일(2026-09-20 23:53:47)을 복사했다.
- 수정 RTL 스냅샷: [`evidence/modified/source/moore_cycle.v`](evidence/modified/source/moore_cycle.v). TB는 정상 원본 스냅샷과 동일하다.
- 수정 로그, VCD, 보고서용 파형: [`evidence/modified/simulation.log`](evidence/modified/simulation.log), [`evidence/modified/wave.vcd`](evidence/modified/wave.vcd), [`evidence/modified/waveform.png`](evidence/modified/waveform.png).
- 복구 로그와 파형: [`evidence/recovered/simulation.log`](evidence/recovered/simulation.log), [`evidence/recovered/wave.vcd`](evidence/recovered/wave.vcd).

파형은 상태 `01`에서 변경 RTL이 `00`을 내는 마지막 구간과 46 ns 실패 경계를 보인다. 교안의 상태, 검사명, 기대 상태와 실패 시각이 캡처와 일치하며 해석상 불확실성은 없다. 작업 트리 RTL은 원복 상태다.
