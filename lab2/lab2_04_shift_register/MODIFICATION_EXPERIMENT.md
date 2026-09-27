# 수정 실험 — 시프트 방향 뒤집기

## 교안 지시와 출처

출처: [`05.LAB2_04_SHIFT_REGISTER_VIVADO.pdf`](../pdf/05.LAB2_04_SHIFT_REGISTER_VIVADO.pdf), 인쇄 쪽수 41. 해당 PDF 페이지를 렌더링해 실험 지시와 수치가 맞는지 확인했다.

교안의 단계는 다음과 같다.

1. 정상 로그와 `wave.vcd`를 보관한다.
2. `shift_register4.v`의 `{serial_in,value[3:1]}`을 `{value[2:0],serial_in}`으로 바꾸고 TB 기대값은 유지한다.
3. 저장 후 `02 Simulate`를 실행해 16 ns의 `input enters MSB` 검사가 실패하는지 확인한다.
4. 첫 입력 1에서 기대값 `1000`과 변경 회로 값 `0001`을 비교한다.
5. RTL을 원복해 저장하고 재실행하여 `checks=8`, 종료 시각 106 ns를 확인한다.

## 변경과 예상 동작

- 변경 RTL: [`src/shift_register4.v`](src/shift_register4.v)의 다음 상태 식을 `{serial_in, value[3:1]}`에서 `{value[2:0], serial_in}`으로 바꿨다.
- 테스트벤치: [`sim/tb_shift_register4.sv`](sim/tb_shift_register4.sv)는 수정하지 않았다. 기대값은 계속 `value=4'b1000`이다.
- 관찰 신호: `clk`, `rst`, `enable`, `serial_in`, `value[3:0]`.
- 예상 실패: 리셋 뒤 첫 `serial_in=1`을 15 ns 상승 에지에서 샘플링하면 변경 회로의 `value`는 `0001`이 된다. TB는 다음 ns인 16 ns에 `1000`을 기대하므로 첫 검사에서 중단된다.

## 실행 결과

| 상태 | 결과 |
|---|---|
| 정상 기준 | `LAB2_PASS shift_register4 checks=8`, 종료 106 ns |
| 방향을 뒤집은 RTL | `LAB2_FAIL input enters MSB time=16000` (16 ns); 기대 `1000`, 실제 `0001` |
| RTL 원복 | `LAB2_PASS shift_register4 checks=8`, 종료 106 ns |

시뮬레이션은 Icarus의 비 GUI 실행으로 수행했다. 수정 RTL 실행은 TB의 `$fatal` 때문에 종료 코드 1로 끝나는 것이 의도된 결과다. 실패 시점까지 기록된 VCD와 로그를 별도 보관했다. RTL은 교안의 복구 절차에 따라 정상 식으로 되돌렸고, 마지막 재실행도 PASS했다.

## 캡처와 재현 자료

- 정상 원본 스냅샷: [`evidence/normal/source/`](evidence/normal/source/) — RTL, TB, 설정, 제약 파일.
- 정상 로그와 파형: [`evidence/normal/simulation.log`](evidence/normal/simulation.log), [`evidence/normal/wave.vcd`](evidence/normal/wave.vcd).
- 정상 스크린샷: [`evidence/normal/normal_screenshot.png`](evidence/normal/normal_screenshot.png). `lab2/images`의 시간순 4번째 파일(2026-09-20 23:52:14)을 복사했다.
- 수정 RTL 스냅샷: [`evidence/modified/source/src/shift_register4.v`](evidence/modified/source/src/shift_register4.v). TB와 나머지 소스는 정상 스냅샷을 사용한다.
- 수정 실험 로그, VCD, 보고서용 파형: [`evidence/modified/simulation.log`](evidence/modified/simulation.log), [`evidence/modified/wave.vcd`](evidence/modified/wave.vcd), [`evidence/modified/waveform.png`](evidence/modified/waveform.png).
- 복구 후 로그와 파형: [`evidence/recovered/simulation.log`](evidence/recovered/simulation.log), [`evidence/recovered/wave.vcd`](evidence/recovered/wave.vcd).

수정 실험 파형에서 15 ns 이후 `value=0001`이고, 16 ns 검사에서 실패한 것이 확인된다. 교안의 연결 변경, 기대값, 실패 시각 사이에 해석상 불확실성은 없었다. 작업 트리의 RTL은 최종적으로 원복된 상태다.
