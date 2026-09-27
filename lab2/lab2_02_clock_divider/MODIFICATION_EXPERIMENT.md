# 수정실험 기록 — 클록 분주기

## 교안 지시

출처: `../pdf/05.LAB2_02_CLOCK_DIVIDER_VIVADO.pdf`, 44쪽. 교안의 지시는 다음과 같다.

1. 정상 로그와 `wave.vcd`를 별도 보관한다.
2. `clock_divider.v`의 상승 조건 `DIVISOR/2 - 1`을 `DIVISOR/2`로 바꾼다.
3. TB는 그대로 두고 저장한 뒤 시뮬레이션한다.
4. minimum divisor duty 검사가 16 ns에 실패하는 이유를 계산한다.
5. 조건을 원복하고 다시 실행해 129개 검사가 통과하는지 확인한다.

## 예상 동작과 수정 결과

수정은 `src/clock_divider.v`의 상승 비교식 한 곳이며, 신호는 `divided`이다. `DIVISOR=10`에서는 rising edge가 한 클록 늦어져 정상 50 ns low / 50 ns high가 60 ns low / 40 ns high가 된다. `DIVISOR=2`에서는 상승 조건이 `count==1`이 되어 하강 조건 `count==DIVISOR-1`과 겹친다. 첫 활성 상승 에지에서 `div2`는 0으로 남지만 검사 기대값은 1이므로 원본 TB가 16 ns에 `minimum divisor duty` 실패를 내는 것이 교안의 의도다. 이 변경 실행은 의도된 FAIL로 기록했고, 교안대로 원래 비교식을 복구한 뒤 재실행해 `LAB2_PASS clock_divider checks=129`를 확인했다.

| 파일/신호 | 변경 또는 관찰 내용 |
|---|---|
| `src/clock_divider.v` | `count == DIVISOR/2 - 1` → `count == DIVISOR/2`로 잠시 변경 후 원복 |
| `sim/tb_clock_divider.sv` | 교안대로 변경하지 않음. `DIVISOR=2`의 `div2` duty 검사에서 16 ns에 실패 |
| 관찰 신호 | `clk`, `rst`, `divided`, `tick`, `div2`, `tick2` |

## 실행·캡처

수정 전 정상 증거와 재현 소스는 `evidence/normal/`에 저장했다. 원본 TB를 그대로 실행한 수정 결과는 `evidence/modified/simulation.log`, `evidence/modified/wave.vcd`, `evidence/modified/clock_divider_modified_waveform.png`에 있다. 보고서 파형은 0–16 ns 구간을 보여 주며, 마지막 검사에서 `div2=0`임을 확인할 수 있다. 변경 실행 뒤 RTL을 복구하고 정상 재실행했으며 복구 로그·VCD는 `evidence/recovered/`에 분리해 두었다. 수정 시점의 RTL 스냅샷은 `evidence/modified/source/`에, 정상 원본은 `evidence/normal/source/`에 있어 양쪽 실행을 재현할 수 있다.
