# 수정 실험 — MSB 대신 LSB 출력하기

## 교안 지시와 출처

출처: [`05.LAB2_05_PISO_VIVADO.pdf`](../pdf/05.LAB2_05_PISO_VIVADO.pdf), 수정 실험 인쇄 쪽수 41 및 해설 인쇄 쪽수 43. 두 페이지를 렌더링해 지시와 예상 실패 정보를 시각적으로 확인했다.

교안의 단계는 다음과 같다.

1. 정상 로그와 파형을 먼저 보관한다.
2. MSB 대신 LSB를 출력하고 TB 기대값은 유지한다.
3. 저장 후 `02 Simulate`를 실행해 `LAB2_FAIL`의 검사 이름과 시각을 읽는다.
4. 어떤 입력과 이전 상태에서 불일치가 생겼는지 계산한다.
5. RTL을 복구해 저장하고 재실행하여 전체 PASS를 확인한다.

해설 쪽은 `assign serial_out = value[3]`을 `value[0]`으로 바꾸면 `word=1`의 첫 출력 검사에서 86 ns에 실패한다고 명시한다. MSB 기대값은 0이고 변경된 LSB 출력은 1이다.

## 변경과 예상 동작

- 변경 RTL: [`src/piso4.v`](src/piso4.v)의 `assign serial_out = value[3]`을 `assign serial_out = value[0]`으로 바꿨다.
- 테스트벤치: [`sim/tb_piso4.sv`](sim/tb_piso4.sv)는 수정하지 않았다. 네 비트를 MSB 우선으로 읽는 기대값을 유지했다.
- 관찰 신호: `clk`, `rst`, `load`, `enable`, `data_in[3:0]`, `value[3:0]`, `serial_out`.
- 예상 실패 원인: `word=0`을 네 번 시프트한 직후 상태는 `0000`이다. 다음 입력 `word=1` (`data_in=0001`)을 로드하면 `value=0001`이 된다. TB의 MSB 우선 첫 비트는 `word[3]=0`이지만, 변경 회로는 `value[0]=1`을 출력한다. 따라서 86 ns 첫 직렬 출력 검사에서 불일치한다.

## 실행 결과

| 상태 | 결과 |
|---|---|
| 정상 기준 | `LAB2_PASS piso4 checks=114`, 종료 976 ns |
| LSB 출력 RTL | `LAB2_FAIL MSB first before edge time=86000` (86 ns); `word=1`, 기대 출력 `0`, 실제 `1` |
| RTL 원복 | `LAB2_PASS piso4 checks=114`, 종료 976 ns |

시뮬레이션은 Icarus의 비 GUI 실행으로 수행했다. 수정 RTL 실행은 TB의 `$fatal` 때문에 종료 코드 1로 끝나는 것이 의도된 결과다. 첫 불일치 시점까지 기록한 VCD와 로그를 별도로 보관했다. RTL은 교안의 복구 절차에 따라 MSB 출력으로 되돌렸고, 마지막 재실행에서 전체 114개 검사가 통과했다.

## 캡처와 재현 자료

- 정상 원본 스냅샷: [`evidence/normal/source/`](evidence/normal/source/) — RTL, TB, 설정, 제약 파일.
- 정상 로그와 파형: [`evidence/normal/simulation.log`](evidence/normal/simulation.log), [`evidence/normal/wave.vcd`](evidence/normal/wave.vcd).
- 정상 스크린샷: [`evidence/normal/normal_screenshot.png`](evidence/normal/normal_screenshot.png). `lab2/images`의 시간순 5번째 파일(2026-09-20 23:53:09)을 복사했다.
- 수정 RTL 스냅샷: [`evidence/modified/source/src/piso4.v`](evidence/modified/source/src/piso4.v). TB와 나머지 소스는 정상 스냅샷을 사용한다.
- 수정 실험 로그, VCD, 보고서용 파형: [`evidence/modified/simulation.log`](evidence/modified/simulation.log), [`evidence/modified/wave.vcd`](evidence/modified/wave.vcd), [`evidence/modified/waveform.png`](evidence/modified/waveform.png).
- 복구 후 로그와 파형: [`evidence/recovered/simulation.log`](evidence/recovered/simulation.log), [`evidence/recovered/wave.vcd`](evidence/recovered/wave.vcd).

수정 실험 파형에는 `word=1` 로드 뒤 `value=0001`, `serial_out=1`이 표시되고 86 ns에 실패 경계가 표시된다. 교안의 수정 대상, `word=1` 검사, 출력 불일치 설명은 일치한다. 작업 트리의 RTL은 최종적으로 원복된 상태다.
