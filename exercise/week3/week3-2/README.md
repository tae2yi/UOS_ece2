# Week 3-2 — 반응 속도 측정기 (LCD)

Combo II-DLD S75용 반응 속도 측정기 RTL입니다. 기존의 7세그먼트 표시 대신 16x2 문자 LCD를 사용하여 상태 메시지와 함께 측정 결과를 표시합니다. 아래 RTL과 XDC로 새 프로젝트를 만들거나, Vivado에서 기존 프로젝트로 열 수 있습니다.

## 보드 조작

| 장치 | 동작 |
|---|---|
| K4 reset | 회로를 초기화합니다. 초기화가 끝나면 LED0가 켜지고 LCD 첫째 줄은 `PRESS N8 TO GO  `이며 둘째 줄은 공백입니다. |
| N8 push button | 켜진 LED0를 끄고 새 라운드를 시작합니다. 1000~10000 ms의 의사 난수 지연 뒤 LED0가 켜지면, 상태 메시지가 `GO! PRESS N8    `로 바뀌고, LED를 본 즉시 N8을 다시 눌러 반응 시간을 멈춥니다. 측정값은 ms 단위로 5자리 숫자로 표시되며, HOLD 상태에서 N8을 다시 누르면 다음 라운드가 시작됩니다. |
| LED0 (N5) | 켜짐은 준비·반응 측정 결과 고정 상태, 꺼짐은 무작위 대기 상태를 뜻합니다. 반응 측정 중에는 켜져 있습니다. |

## LCD 표시

| 상태 | LCD 첫째 줄 | LCD 둘째 줄 |
|---|---|---|
| READY (초기화 완료, 대기) | `PRESS N8 TO GO  ` | 공백 (16개 스페이스) |
| WAITING (무작위 대기 중) | `WAIT...         ` | 공백 (16개 스페이스) |
| REACTING (반응 시간 측정 중) | `GO! PRESS N8    ` | 공백 (16개 스페이스) |
| HOLD (측정 완료, 결과 표시) | `REACTION TIME   ` | `TIME: nnnnn ms  ` (5자리 숫자) |

HOLD 상태의 둘째 줄은 `TIME: ` 다음 5자리 밀리초 값이 0으로 채워진 형식입니다. 예를 들어 반응시간 123 ms는 `TIME: 00123 ms  `로 표시됩니다.

무작위 대기 중 누른 N8은 무시됩니다. LED0가 켜진 뒤 다시 눌러야 측정이 끝납니다. 라운드를 시작한 뒤부터 두 번째 N8 입력이 들어오기 전까지 LCD 둘째 줄은 공백을 유지합니다. LED0가 다시 켜진 것을 보고 N8을 누르는 순간 측정이 멈추고, HOLD 상태에 진입하며 결과가 화면에 나타납니다. 결과와 켜진 LED0는 다음 N8 입력까지 그대로 유지됩니다.

## Vivado에서 열기

1. 새 프로젝트가 필요하면 **Create Project**에서 RTL Project를 만들고 부품을 `xc7s75fgga484-1`로 선택합니다.
2. `src/`의 다섯 `.v` 파일을 Design Sources에 추가합니다. **Design top은 `reaction_timer_lcd`**입니다.
3. `constraints/reaction_timer_lcd.xdc`를 Constraints에 추가합니다. 포트명을 유지하고, B6 입력 클록을 **1 kHz**로 설정하세요. 한 클록이 1 ms에 해당하므로 다른 주파수를 쓰면 측정 단위와 대기 시간이 달라집니다.
4. `sim/tb_reaction_timer_lcd.sv`는 시뮬레이션 소스로 추가하고, 시뮬레이션 top으로 `tb_reaction_timer_lcd`를 선택합니다. 이 파일은 보드 설계 top이 아닙니다.
5. RTL 수정 전 결과가 남아 있다면 **Reset Runs**로 `synth_1`과 `impl_1`을 초기화한 뒤 Synthesis, Implementation, bitstream을 다시 생성하고 보드에 프로그램합니다.
6. Vivado 프로젝트 폴더는 `vivado/` 디렉토리에 생성하면 됩니다.

## 파일 구성

| 경로 | 역할 |
|---|---|
| `src/input_frontend.v` | reset 동기화, N8 2단 동기화, 첫 상승 에지 펄스와 안정 release 후 재무장 |
| `src/reaction_core.v` | free-running LFSR, 1000~10000 ms 대기, 반응 시간 카운트와 결과 고정 (17비트 제한) |
| `src/binary_to_bcd5.v` | 17비트 밀리초 값을 5자리 십진 BCD로 변환 (99999 ms 최대값) |
| `src/lcd_reaction.v` | HD44780 호환 16x2 LCD 드라이버, 4상 바이트 쓰기 타이밍 |
| `src/reaction_timer_lcd.v` | 보드 top, 입력·코어·표시기 연결 |
| `constraints/reaction_timer_lcd.xdc` | S75의 B6/K4/N8, LED0, LCD 데이터/제어 핀과 1 kHz 클록 제약 |
| `sim/tb_reaction_timer_lcd.sv` | reset, 버튼 bounce·재무장, 라운드 시작, 대기, 반응 측정, LCD 버스 디코딩, 결과 검증 |
| `simulation.json` | RTL 소스와 self-checking 테스트벤치 목록 |

반응 카운터는 5자리 표시 범위인 99,999 ms에서 포화합니다. `RELEASE_STABLE_CYCLES`의 기본값은 5입니다. 버튼 입력은 2단 플립플롭으로 동기화하고, 동기화된 첫 상승 에지에서 한 번의 press 펄스를 만듭니다. 새 입력은 동기화된 low가 연속 5클록(5 ms) 관측된 뒤에만 다시 받을 수 있습니다. 이 release 확인은 누름에 추가 지연을 주지 않고 버튼 bounce로 중복 라운드가 시작되는 것을 막습니다. `RELEASE_STABLE_CYCLES`가 0 이하로 설정되면 최소 1클록으로 처리합니다. 무작위 지연은 기본 `MIN_DELAY_MS=1000`, `MAX_DELAY_MS=10000` 범위이며, 최대값이 최소값보다 작으면 최소값으로 보정합니다.

## 시뮬레이션

사전 합성 시뮬레이션을 실행하려면:

```
python3 tools/lab1.py simulate
```

이 명령어는 iverilog와 vvp를 사용하여 자동으로 컴파일하고 테스트벤치를 실행합니다. iverilog가 설치되지 않았다면 직접 실행할 수도 있습니다:

```
iverilog -g2012 -Wall -I src -I sim -s tb_reaction_timer_lcd -o /tmp/sim.vvp \
  src/input_frontend.v src/reaction_core.v src/binary_to_bcd5.v \
  src/lcd_reaction.v src/reaction_timer_lcd.v sim/tb_reaction_timer_lcd.sv
vvp -N /tmp/sim.vvp
```

성공하면 `LAB_PASS reaction_timer_lcd checks=NN` 메시지가 출력되고 정상 종료됩니다.

## 상태 전이

회로의 상태 흐름은 다음과 같습니다:

1. **READY**: 초기화 완료, LED0 켜짐, LCD는 `PRESS N8 TO GO  ` 표시.
2. **N8 첫 입력**: LED0 꺼지고, 1000~10000 ms 의사 난수 대기 시작, 상태는 WAITING 진입.
3. **WAITING**: LED0 끔, LCD는 `WAIT...         ` 표시. 이 상태에서 N8 입력은 무시됨.
4. **대기 만료**: LED0 켜짐, 상태는 REACTING 진입, LCD는 `GO! PRESS N8    ` 표시.
5. **REACTING**: LED0 켜짐, 버튼 누름까지 반응 시간 카운팅. 이 상태에서 LCD 둘째 줄은 공백 유지.
6. **N8 두 번째 입력**: 측정된 반응 시간을 저장하고 상태는 HOLD 진입, LCD에 결과 표시.
7. **HOLD**: LED0 켜짐, LCD는 `REACTION TIME   ` (첫째 줄)과 `TIME: nnnnn ms  ` (둘째 줄) 표시. 결과는 유지.
8. **다시 N8 입력**: 새 라운드 시작, 상태는 READY에서 WAITING으로 진입.

측정값은 LED0가 켜지는 클록 에지를 `t=0`으로 두고, 버튼이 누르는 순간을 기준으로 경과한 클록 수입니다. 예를 들어, LED0가 켜진 직후 다음 클록 상승 에지에서 눌리면 1 ms가 기록됩니다.
