# 수정실험 기록 — 레지스터 쌍

## 교안 지시

출처: `../pdf/05.LAB2_03_REGISTER_VIVADO.pdf`, 43쪽. 교안의 지시는 다음과 같다.

1. 정상 로그와 `wave.vcd`를 보관한다.
2. `register_pair.v`의 `value <= stored`를 `value <= data_in`으로 바꾼다. TB는 바꾸지 않는다.
3. 저장 후 시뮬레이션하고, 26 ns의 `transfer stored not live input` 검사가 실패하는지 확인한다.
4. 그 순간 기대값 A와 잘못 전달된 입력 3을 비교한다.
5. RTL을 원복하고 다시 실행해 `checks=7` 통과를 확인한다.

## 예상 동작과 수정 결과

잠시 바꾼 파일은 `src/register_pair.v` 한 곳이다. 15 ns에 저장된 값은 `stored=A`이고, 다음 전달 에지 전 `data_in=3`으로 바뀐다. 정상 회로는 25 ns 에지 뒤 `value=A`를 유지해 `{stored,value}=8'hAA`가 되어야 한다. 수정 회로는 live input `3`을 전달해 `{stored,value}=8'hA3`가 되고, TB는 26 ns에 `transfer stored not live input` 검사에서 실패한다. 이는 의도된 수정실험 FAIL이다. 교안대로 RTL을 원복한 뒤 재실행하여 `LAB2_PASS register_pair checks=7`을 확인했다.

| 파일/신호 | 변경 또는 관찰 내용 |
|---|---|
| `src/register_pair.v` | `value <= stored` → `value <= data_in`으로 잠시 변경 후 원복 |
| `sim/tb_register_pair.sv` | 교안대로 변경하지 않음. 기존 7개 self-check 유지 |
| 관찰 신호 | `clk`, `rst`, `load`, `transfer`, `data_in[3:0]`, `stored[3:0]`, `value[3:0]` |

## 실행·캡처

수정 전 정상 로그, VCD, 화면 캡처와 재현 소스는 `evidence/normal/`에 있다. 원본 TB로 실행한 수정 결과는 `evidence/modified/simulation.log`, `evidence/modified/wave.vcd`, `evidence/modified/register_pair_modified_waveform.png`에 저장했다. PNG는 0–26 ns를 보여 주며 25 ns 전달 에지에서 `data_in=3`, `stored=A`, `value=3`을 읽을 수 있다. 이어 RTL을 복구하고 정상 재실행했으며 복구 결과는 `evidence/recovered/`에 분리 보관했다. 수정 시점의 RTL 스냅샷은 `evidence/modified/source/`에, 정상 원본은 `evidence/normal/source/`에 있다.
