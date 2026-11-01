# FPGA 추가 실습 · 모듈과 테스트벤치

[실습 목차](index.md)

장비와 함께 제공된 교재를 보고, 주차별 매뉴얼에 지정된 순서대로 각자 시뮬레이션과 실제 보드 시연을 수행한다. 이 문서의 항목 번호는 소스 참조용이다. 원본 장비 예제를 바탕으로 기능별 모듈을 나누고 검증용 테스트벤치를 작성했다. 이 문서의 코드는 원본 그대로의 복사본이 아니다.

## 코드 사용 방법

- 설계 모듈과 테스트벤치는 아래 콜아웃에 수록했다. 해당 실습의 설계 모듈을 모두 실습 프로젝트에 복사해 사용한다. 최상위 모듈은 하위 모듈을 연결한다.
- 테스트벤치는 시뮬레이션 전용 SystemVerilog 코드다. 입력을 주고 예상 출력과 다르면 오류를 낸다. 보드에 올릴 때는 TB를 제외하고 설계의 최상위 모듈을 선택한다.
- 클록을 사용하는 설계의 기본 입력은 `clk_50mhz`와 HIGH 활성 `rst_p`다. TB에서는 입력을 클록 하강 에지에 바꾸고, 상승 에지 후 결과를 읽어 설계와 입력의 실행 순서가 충돌하지 않게 한다.
- TB의 시간 관련 매개변수는 실행을 빠르게 하기 위해 줄였다. TB에서의 10 ns 클록은 모의 실행용이며, 축소된 클록 수 검증이 실제 보드의 초·주파수 측정을 대신하지 않는다.
- 보드 핀은 교재와 장비 핀맵을 보고 연결한다. 이 자료에는 XDC를 포함하지 않았다. 버튼의 원시 신호를 한 번 누름 펄스로 만드는 처리는 기존 실습 코드를 연결한다.

> [!NOTE]
> **검증 범위:** Icarus Verilog로 8개 테스트벤치가 모두 PASS했다. Vivado 합성·타이밍 확인이나 실제 보드 시연은 아직 수행하지 않았다. SRAM·ADC·DAC의 TB 장치 모델은 디지털 동작을 확인하며 실제 장치의 모든 시간 조건과 아날로그 동작을 재현하지 않는다.

## 코드에서 사용하는 표현

| 표현 | 뜻 |
|---|---|
| `module ... endmodule` | 입출력과 기능을 묶은 회로 단위 |
| `u_...` | 하위 모듈을 연결한 회로의 이름 |
| `wire` | 회로 사이를 연결하는 신호 |
| `reg` | always 블록에서 값을 대입할 신호 · 항상 실제 레지스터가 되는 것은 아님 |
| `parameter` | 모듈을 연결할 때 지정하는 상수 |
| `always @*` | 입력이 바뀌면 출력 값을 계산하는 조합회로 |
| `always @(posedge clk_50mhz)` | 클록 상승 에지에서 값을 갱신하는 순차회로 |
| `<=` | 순차회로에서 사용하는 비차단 대입 |
| `!==` | TB에서 X·Z 상태까지 포함해 서로 다른지 검사 |
| `#1` | TB에서 시뮬레이션 시간 1 ns 기다리기 |
| `$fatal` | 예상과 다르면 오류로 시뮬레이션 종료 |
| `$display`, `$finish` | 메시지 출력, 시뮬레이션 종료 |

## 시뮬레이션 방법

1. 해당 실습의 **설계 모듈 콜아웃을 모두** 실습 프로젝트에 추가한다.
2. **테스트벤치 콜아웃**을 시뮬레이션 소스로 추가하고, 시뮬레이션 최상위는 `tb`로 선택한다. 실습마다 tb라는 이름을 사용하므로 한 번에 한 실습씩 실행한다.
3. 실행 결과의 `PASS` 메시지와 파형을 확인한다. 예상과 다르면 TB가 오류 메시지를 출력하고 종료한다.
4. 보드 시연 때는 TB를 제외하고 해당 설계의 최상위 모듈을 선택한다.

| 주차 | 실습 | 설계 최상위 모듈 |
|---|---|---|
| STM32_0 | 4비트 곱셈기 | `mult_4bit` |
| STM32_0 | BCD를 이진수로 변환 | `bcd_conv` |
| STM32_1 | 피아노 | `piano` |
| STM32_1 | 신호등 제어 | `traffic` |
| STM32_2 | 서보모터 제어 | `servo_ctrl` |
| STM32_2 | SRAM 읽기·쓰기 | `sram` |
| STM32_1 | ADC | `adc` |
| STM32_2 | DAC | `dac` |

## 1. 4비트 곱셈기 · STM32_0

**모듈 역할:** multiply_unsigned: 실제 곱셈 / mult_4bit: 4비트 입출력 연결

**TB 검사:** 256개 입력 조합의 8비트 결과

**원본과의 차이·연결 조건:** 기존 예제와 같은 곱셈 기능이다.


### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module mult_4bit(input wire [3:0] a, b, output wire [7:0] m);
>     multiply_unsigned #(.WIDTH(4)) u_multiply(a, b, m);
> endmodule
>
> ```

### 설계 모듈 · multiply_unsigned

> [!TIP]
> **설계 모듈 · multiply_unsigned**
>
> ```verilog
> `timescale 1ns/1ps
> // 4비트 곱셈: 입력 두 개를 곱해 8비트 결과를 만듭니다.
> module multiply_unsigned #(parameter WIDTH = 4)(
>     input wire [WIDTH-1:0] a, b,
>     output wire [2*WIDTH-1:0] product
> );
>     assign product = a * b;
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg [3:0] a, b;
>     wire [7:0] m;
>     mult_4bit dut(a, b, m);
>     integer x, y;
>     initial begin
>         for (x=0; x<16; x=x+1)
>             for (y=0; y<16; y=y+1) begin
>                 a=x; b=y; #1;
>                 if (m !== x*y) $fatal(1, "multiply a=%0d b=%0d m=%0d", x,y,m);
>             end
>         $display("PASS multiplier: 256 input pairs"); $finish;
>     end
>     initial begin #1000; $fatal(1, "timeout"); end
> endmodule
>
> ```

## 2. BCD를 이진수로 변환 · STM32_0

**모듈 역할:** bcd_to_binary: 변환과 유효성 검사 / bcd_conv: 입출력 연결

**TB 검사:** 유효한 100개 입력과 범위를 벗어난 156개 입력

**원본과의 차이·연결 조건:** valid 출력을 추가했다. 각 자리의 0~9 입력일 때만 valid가 1이다.


### 설계 모듈 · bcd_to_binary

> [!TIP]
> **설계 모듈 · bcd_to_binary**
>
> ```verilog
> `timescale 1ns/1ps
> // 십의 자리와 일의 자리를 각각 0~9로 입력합니다.
> module bcd_to_binary(
>     input wire [3:0] ten, one,
>     output wire [6:0] binary,
>     output wire valid
> );
>     assign binary = ten * 7'd10 + one;
>     assign valid = (ten <= 9) && (one <= 9);
> endmodule
>
> ```

### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module bcd_conv(
>     input wire [3:0] one, ten,
>     output wire [6:0] bin,
>     output wire valid
> );
>     bcd_to_binary u_convert(ten, one, bin, valid);
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg [3:0] ten, one;
>     wire [6:0] bin;
>     wire valid;
>     bcd_conv dut(one, ten, bin, valid);
>     integer t, o;
>     initial begin
>         for(t=0;t<16;t=t+1)
>             for(o=0;o<16;o=o+1) begin
>                 ten=t; one=o; #1;
>                 if(valid !== ((t<10)&&(o<10))) $fatal(1,"BCD valid");
>                 if(t<10 && o<10 && bin !== t*10+o) $fatal(1,"BCD value");
>             end
>         $display("PASS BCD: 100 valid and 156 invalid inputs"); $finish;
>     end
>     initial begin #1000; $fatal(1,"timeout"); end
> endmodule
>
> ```

## 3. 피아노 · STM32_1

**모듈 역할:** note_select: 음계 선택 / square_tone: 사각파 생성 / piano: 연결

**TB 검사:** 8개 음의 반주기, 무입력, 여러 버튼 입력, 리셋

**원본과의 차이·연결 조건:** 원본의 1 MHz 클록과 분주값 대신 50 MHz와 음의 주파수로 반주기를 계산한다. key는 HIGH 활성의 안정된 입력이며 여러 키가 눌리면 무음이다.


### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module piano #(parameter CLK_HZ=50_000_000)(
>     input wire clk_50mhz, rst_p,
>     input wire [7:0] key,
>     output wire piezo
> );
>     wire [31:0] frequency_hz;
>     note_select u_note(key, frequency_hz);
>     square_tone #(.CLK_HZ(CLK_HZ)) u_tone(clk_50mhz,rst_p,frequency_hz,piezo);
> endmodule
>
> ```

### 설계 모듈 · note_select

> [!TIP]
> **설계 모듈 · note_select**
>
> ```verilog
> `timescale 1ns/1ps
> // 버튼 입력에 대응하는 음의 주파수를 선택합니다.
> // 보드의 버튼 입력은 안정된 HIGH 활성 신호로 전달합니다.
> module note_select(input wire [7:0] key, output reg [31:0] frequency_hz);
>     always @* begin
>         case(key)
>             8'h80: frequency_hz=262;
>             8'h40: frequency_hz=294;
>             8'h20: frequency_hz=330;
>             8'h10: frequency_hz=349;
>             8'h08: frequency_hz=392;
>             8'h04: frequency_hz=440;
>             8'h02: frequency_hz=494;
>             8'h01: frequency_hz=523;
>             default: frequency_hz=0; // 무입력이나 여러 버튼 입력은 무음
>         endcase
>     end
> endmodule
>
> ```

### 설계 모듈 · square_tone

> [!TIP]
> **설계 모듈 · square_tone**
>
> ```verilog
> `timescale 1ns/1ps
> module square_tone #(parameter CLK_HZ=50_000_000)(
>     input wire clk_50mhz, rst_p,
>     input wire [31:0] frequency_hz,
>     output reg tone
> );
>     reg [31:0] count, previous_hz;
>     wire [31:0] half_cycles = frequency_hz == 0 ? 1 :
>                              CLK_HZ / (2 * frequency_hz);
>     always @(posedge clk_50mhz) begin
>         if(rst_p) begin count<=0; tone<=0; previous_hz<=0; end
>         else if(frequency_hz==0 || frequency_hz!=previous_hz) begin
>             count<=0; tone<=0; previous_hz<=frequency_hz;
>         end
>         else if(count >= half_cycles-1) begin count<=0; tone<=~tone; end
>         else count<=count+1;
>     end
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg clk=0, rst=1;
>     always #5 clk=~clk;
>     reg [7:0] key=0;
>     wire piezo;
>     reg [7:0] select_key;
>     wire [31:0] frequency_hz;
>     note_select select_dut(select_key,frequency_hz);
>     piano #(.CLK_HZ(10000)) dut(clk,rst,key,piezo);
>     integer notes[0:7];
>     integer n, j, half_cycles;
>     reg expected;
>     task step; begin @(posedge clk); #1; end endtask
>     initial begin
>         notes[0]=262; notes[1]=294; notes[2]=330; notes[3]=349;
>         notes[4]=392; notes[5]=440; notes[6]=494; notes[7]=523;
>         step; @(negedge clk); rst=0;
>         for(n=0;n<8;n=n+1) begin
>             select_key=8'h80 >> n; #1;
>             if(frequency_hz !== notes[n]) $fatal(1,"note lookup");
>             @(negedge clk); key=8'h80 >> n; step;
>             if(piezo !== 0) $fatal(1,"note change reset");
>             half_cycles=10000/(2*notes[n]);
>             expected=0;
>             for(j=1;j<=4*half_cycles;j=j+1) begin
>                 step;
>                 if(j%half_cycles==0) expected=~expected;
>                 if(piezo !== expected) $fatal(1,"tone timing note=%0d",n);
>             end
>         end
>         @(negedge clk); key=8'hC0; select_key=8'hC0; step;
>         if(piezo !== 0 || frequency_hz !== 0) $fatal(1,"multiple keys");
>         @(negedge clk); key=0; select_key=0;
>         repeat(40) begin step; if(piezo !== 0) $fatal(1,"silence"); end
>         @(negedge clk); rst=1; step;
>         if(piezo !== 0) $fatal(1,"reset");
>         $display("PASS piano: all 8 tones, silence, multiple keys, reset"); $finish;
>     end
>     initial begin #100000; $fatal(1,"timeout"); end
> endmodule
>
> ```

## 4. 신호등 제어 · STM32_1

**모듈 역할:** second_tick: 1초 기준과 점멸 / traffic_sequence: 방향과 단계 / traffic_lights: LED 출력 / traffic: 연결

**TB 검사:** 네 방향의 13단계, 보행자 점멸, 점멸 모드, 리셋

**원본과의 차이·연결 조건:** flicker는 HIGH이면 점멸 모드를 유지하는 입력이다. 원본의 별도 수동 점멸 버튼 토글 로직은 포함하지 않았다. 출력 1은 논리적인 켜짐이며 장비 LED의 실제 극성은 핀 연결 단계에서 맞춘다.


### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module traffic #(parameter CLK_HZ=50_000_000)(
>     input wire clk_50mhz,rst_p,flicker,
>     output wire [3:0] led_red,led_yellow,led_green,led_left,
>     output wire [3:0] led_walk_red,led_walk_green
> );
>     wire tick,blink;
>     wire [1:0] direction;
>     wire [3:0] phase;
>     second_tick #(.CLK_HZ(CLK_HZ)) u_tick(clk_50mhz,rst_p,tick,blink);
>     traffic_sequence u_sequence(clk_50mhz,rst_p,tick,flicker,direction,phase);
>     traffic_lights u_lights(direction,phase,flicker,blink,
>         led_red,led_yellow,led_green,led_walk_red,led_walk_green);
>     assign led_left=led_green;
> endmodule
>
> ```

### 설계 모듈 · second_tick

> [!TIP]
> **설계 모듈 · second_tick**
>
> ```verilog
> `timescale 1ns/1ps
> // 느린 동작은 새 클록 대신 한 클록 길이의 tick으로 만듭니다.
> module second_tick #(parameter CLK_HZ=50_000_000)(
>     input wire clk_50mhz, rst_p,
>     output wire tick,
>     output wire blink
> );
>     reg [31:0] count;
>     assign tick=(count==CLK_HZ-1);
>     assign blink=(count < CLK_HZ/2);
>     always @(posedge clk_50mhz)
>         if(rst_p || tick) count<=0;
>         else count<=count+1;
> endmodule
>
> ```

### 설계 모듈 · traffic_lights

> [!TIP]
> **설계 모듈 · traffic_lights**
>
> ```verilog
> `timescale 1ns/1ps
> module traffic_lights(
>     input wire [1:0] direction,
>     input wire [3:0] phase,
>     input wire flicker,blink,
>     output reg [3:0] red,yellow,green,walk_red,walk_green
> );
>     reg [3:0] vehicle_mask,pedestrian_mask;
>     always @* begin
>         // 방향별 차량과 보행자 LED를 선택합니다.
>         case(direction)
>             0: begin vehicle_mask=4'b1000; pedestrian_mask=4'b0100; end
>             1: begin vehicle_mask=4'b0100; pedestrian_mask=4'b0010; end
>             2: begin vehicle_mask=4'b0010; pedestrian_mask=4'b0001; end
>             3: begin vehicle_mask=4'b0001; pedestrian_mask=4'b1000; end
>         endcase
>         red=4'b1111; yellow=0; green=0; walk_red=4'b1111; walk_green=0;
>         if(flicker) begin
>             red=0; yellow={4{blink}}; walk_red={4{blink}};
>         end else begin
>             if(phase<=10) begin green=vehicle_mask; red=~vehicle_mask; end
>             else begin yellow=vehicle_mask; red=~vehicle_mask; end
>             if(phase<=3) begin walk_green=pedestrian_mask; walk_red=~pedestrian_mask; end
>             else if(phase<=10) begin
>                 walk_green=blink ? pedestrian_mask : 4'b0000;
>                 walk_red=~pedestrian_mask;
>             end
>         end
>     end
> endmodule
>
> ```

### 설계 모듈 · traffic_sequence

> [!TIP]
> **설계 모듈 · traffic_sequence**
>
> ```verilog
> `timescale 1ns/1ps
> // 각 방향에서 0~10초는 초록, 11~12초는 노랑입니다.
> module traffic_sequence(
>     input wire clk_50mhz,rst_p,tick,flicker,
>     output reg [1:0] direction,
>     output reg [3:0] phase
> );
>     always @(posedge clk_50mhz) begin
>         if(rst_p || flicker) begin direction<=0; phase<=0; end
>         else if(tick)
>             if(phase==12) begin phase<=0; direction<=direction+1'b1; end
>             else phase<=phase+1'b1;
>     end
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg clk=0,rst=1,flicker=0;
>     always #5 clk=~clk;
>     wire [3:0] red,yellow,green,left,wr,wg;
>     traffic #(.CLK_HZ(4)) dut(clk,rst,flicker,red,yellow,green,left,wr,wg);
>     integer direction,phase,subcycle;
>     reg [3:0] vm,pm,er,ey,eg,ewr,ewg;
>     task step; begin @(posedge clk); #1; end endtask
>     task check;
>         begin
>             case(direction)
>                 0: begin vm=8; pm=4; end
>                 1: begin vm=4; pm=2; end
>                 2: begin vm=2; pm=1; end
>                 3: begin vm=1; pm=8; end
>             endcase
>             er=~vm; ey=0; eg=0; ewr=15; ewg=0;
>             if(phase<11) eg=vm; else ey=vm;
>             if(phase<4) begin ewg=pm; ewr=~pm; end
>             else if(phase<11) begin
>                 ewr=~pm; if(subcycle<2) ewg=pm;
>             end
>             if({red,yellow,green,wr,wg} !== {er,ey,eg,ewr,ewg})
>                 $fatal(1,"traffic dir=%0d phase=%0d sub=%0d",direction,phase,subcycle);
>             if(left !== green) $fatal(1,"left indicator");
>         end
>     endtask
>     initial begin
>         step; @(negedge clk); rst=0;
>         // 네 방향의 13단계와 각 초의 점멸을 확인합니다.
>         for(direction=0;direction<4;direction=direction+1)
>             for(phase=0;phase<13;phase=phase+1)
>                 for(subcycle=0;subcycle<4;subcycle=subcycle+1) begin
>                     check; step;
>                 end
>         direction=0; phase=0; subcycle=0; check;
>         @(negedge clk); flicker=1; step;
>         repeat(8) begin
>             if(red !== 0 || green !== 0 || wg !== 0) $fatal(1,"flicker outputs");
>             if(yellow !== wr || !(yellow===0 || yellow===15)) $fatal(1,"flicker blink");
>             step;
>         end
>         @(negedge clk); flicker=0; rst=1; step;
>         direction=0; phase=0; subcycle=0; check;
>         $display("PASS traffic: full cycle, pedestrian blink, flicker, reset"); $finish;
>     end
>     initial begin #100000; $fatal(1,"timeout"); end
> endmodule
>
> ```

## 5. 서보모터 제어 · STM32_2

**모듈 역할:** servo_position: 위치 변경 / servo_pwm: 펄스 생성 / servo_ctrl: 연결

**TB 검사:** 20 ms 프레임의 클록 수, 1·1.5·2 ms 폭에 대응하는 클록 수, 위치 제한, 동시 입력, 리셋

**원본과의 차이·연결 조건:** 원본의 0.7~2.3 ms 폭 대신 1~2 ms 범위에서 0.1 ms씩 변경한다. left_pulse와 right_pulse는 버튼 한 번당 한 클록 길이의 펄스다. 새 폭은 다음 20 ms 프레임부터 적용된다.


### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module servo_ctrl #(parameter CLK_HZ=50_000_000)(
>     input wire clk_50mhz,rst_p,left_pulse,right_pulse,
>     output wire servo
> );
>     wire [31:0] pulse_us;
>     servo_position u_position(clk_50mhz,rst_p,left_pulse,right_pulse,pulse_us);
>     servo_pwm #(.CLK_HZ(CLK_HZ)) u_pwm(clk_50mhz,rst_p,pulse_us,servo);
> endmodule
>
> ```

### 설계 모듈 · servo_position

> [!TIP]
> **설계 모듈 · servo_position**
>
> ```verilog
> `timescale 1ns/1ps
> // 버튼은 동기화·디바운스 후 한 클록 길이의 펄스로 전달합니다.
> module servo_position(
>     input wire clk_50mhz,rst_p,left_pulse,right_pulse,
>     output reg [31:0] pulse_us
> );
>     always @(posedge clk_50mhz)
>         if(rst_p) pulse_us<=1500;
>         else if(left_pulse && !right_pulse && pulse_us>1000) pulse_us<=pulse_us-100;
>         else if(right_pulse && !left_pulse && pulse_us<2000) pulse_us<=pulse_us+100;
> endmodule
>
> ```

### 설계 모듈 · servo_pwm

> [!TIP]
> **설계 모듈 · servo_pwm**
>
> ```verilog
> `timescale 1ns/1ps
> module servo_pwm #(parameter CLK_HZ=50_000_000)(
>     input wire clk_50mhz,rst_p,
>     input wire [31:0] pulse_us,
>     output wire servo
> );
>     localparam FRAME_CYCLES=CLK_HZ/50; // 20 ms
>     reg [31:0] count;
>     reg [31:0] width_cycles;
>     always @(posedge clk_50mhz) begin
>         if(rst_p) begin count<=0; width_cycles<=(CLK_HZ/1000)*3/2; end
>         else if(count==FRAME_CYCLES-1) begin
>             count<=0;
>             // 프레임 경계에서만 폭을 바꿔 중간 펄스가 잘리지 않게 합니다.
>             width_cycles<=pulse_us*(CLK_HZ/1000)/1000;
>         end
>         else count<=count+1;
>     end
>     assign servo=!rst_p && (count<width_cycles);
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg clk=0,rst=1,l=0,r=0;
>     always #5 clk=~clk;
>     wire [31:0] us;
>     wire servo;
>     servo_position position_dut(clk,rst,l,r,us);
>     servo_pwm #(.CLK_HZ(100000)) pwm_dut(clk,rst,us,servo);
>     integer i,high_count;
>     task step; begin @(posedge clk); #1; end endtask
>     task press(input bit left_button,input bit right_button);
>         begin
>             @(negedge clk); l=left_button; r=right_button; step;
>             @(negedge clk); l=0; r=0;
>         end
>     endtask
>     task check_frame(input integer expected_high);
>         begin
>             // 폭이 적용된 새 프레임부터 한 프레임 전체를 셉니다.
>             @(posedge servo); #1;
>             high_count=0;
>             for(i=0;i<2000;i=i+1) begin
>                 if(servo) high_count=high_count+1;
>                 step;
>             end
>             if(high_count != expected_high)
>                 $fatal(1,"servo width expected=%0d got=%0d",expected_high,high_count);
>         end
>     endtask
>     initial begin
>         step; if(us!==1500 || servo!==0) $fatal(1,"servo reset");
>         @(negedge clk); rst=0;
>         check_frame(150);
>         repeat(8) press(1,0);
>         if(us!==1000) $fatal(1,"left limit");
>         check_frame(100);
>         repeat(15) press(0,1);
>         if(us!==2000) $fatal(1,"right limit");
>         check_frame(200);
>         press(1,1);
>         if(us!==2000) $fatal(1,"both buttons");
>         @(negedge clk); rst=1; step;
>         if(us!==1500 || servo!==0) $fatal(1,"reset after running");
>         $display("PASS servo: 20ms frame, 1/1.5/2ms pulse, limits, reset"); $finish;
>     end
>     initial begin #300000; $fatal(1,"timeout"); end
> endmodule
>
> ```

## 6. SRAM 읽기·쓰기 · STM32_2

**모듈 역할:** sram_bus_control: 읽기·쓰기와 버스 방향 / sram: 주소와 데이터 연결

**TB 검사:** 16개 주소의 저장·읽기, 미사용 시 Z, 읽기·쓰기 동시 요청

**원본과의 차이·연결 조건:** 원본과 달리 읽기·쓰기 동시 요청은 무시한다. 외부 메모리 버스는 16비트이고 이번 실습은 주소 0~15와 데이터 하위 4비트를 사용한다. 실제 SRAM의 접근·설정·유지 시간 검증은 별도다.


### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module sram(
>     input wire ctrl_w,ctrl_r,
>     input wire [3:0] address,data_in,
>     output wire ram_cs,ram_oe,ram_we,
>     output wire [17:0] ram_address,
>     inout wire [15:0] ram_data,
>     output wire [7:0] led_out
> );
>     wire drive_data,read_data;
>     sram_bus_control u_control(ctrl_w,ctrl_r,drive_data,read_data,ram_cs,ram_oe,ram_we);
>     assign ram_address={14'b0,address};
>     assign ram_data=drive_data ? {12'b0,data_in} : 16'bz;
>     assign led_out=read_data ? {4'b0,ram_data[3:0]} : 8'b0;
> endmodule
>
> ```

### 설계 모듈 · sram_bus_control

> [!TIP]
> **설계 모듈 · sram_bus_control**
>
> ```verilog
> `timescale 1ns/1ps
> // SRAM 버스는 읽을 때 FPGA가 구동하지 않고 Z 상태로 놓습니다.
> // ctrl_w와 ctrl_r가 동시에 들어오면 둘 다 수행하지 않습니다.
> module sram_bus_control(
>     input wire ctrl_w,ctrl_r,
>     output wire drive_data,read_data,
>     output wire ram_cs,ram_oe,ram_we
> );
>     assign drive_data=ctrl_w && !ctrl_r;
>     assign read_data=ctrl_r && !ctrl_w;
>     assign ram_cs=!(drive_data || read_data);
>     assign ram_oe=!read_data;
>     assign ram_we=!drive_data;
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> // 간단한 비동기 SRAM 모델. 실제 장치의 ns 단위 접근 시간은 별도입니다.
> module sram_model(
>     input wire cs_n,oe_n,we_n,
>     input wire [17:0] address,
>     inout wire [15:0] data
> );
>     reg [15:0] memory[0:15];
>     assign data=(!cs_n && !oe_n && we_n) ? memory[address[3:0]] : 16'bz;
>     always @(negedge we_n) begin
>         #1;
>         if(!cs_n && !we_n) memory[address[3:0]]=data;
>     end
> endmodule
>
> module tb;
>     reg wr=0,rd=0;
>     reg [3:0] address=0,data_in=0;
>     wire cs_n,oe_n,we_n;
>     wire [17:0] ram_address;
>     wire [15:0] bus;
>     wire [7:0] led;
>     sram dut(wr,rd,address,data_in,cs_n,oe_n,we_n,ram_address,bus,led);
>     sram_model memory(cs_n,oe_n,we_n,ram_address,bus);
>     integer i;
>     initial begin
>         #2;
>         if(bus !== 16'bz || led !== 0) $fatal(1,"idle");
>         for(i=0;i<16;i=i+1) begin
>             address=i; data_in=15-i; #2;
>             wr=1; #2;
>             if(bus !== 15-i || ram_address !== i) $fatal(1,"write bus");
>             wr=0; #2;
>         end
>         for(i=0;i<16;i=i+1) begin
>             address=i; rd=1; #2;
>             if(led !== 15-i || bus !== 15-i) $fatal(1,"read address=%0d",i);
>             rd=0; #2;
>         end
>         wr=1; rd=1; #2;
>         if(bus !== 16'bz || {cs_n,oe_n,we_n} !== 3'b111) $fatal(1,"conflict");
>         $display("PASS SRAM: 16 addresses, bus release, simultaneous request"); $finish;
>     end
>     initial begin #1000; $fatal(1,"timeout"); end
> endmodule
>
> ```

## 7. ADC · STM32_1

**모듈 역할:** adc_command: 채널 선택 명령 / serial_frame16: 16비트 송수신 / adc: 변환 결과 저장

**TB 검사:** 3개 프레임의 명령 비트·채널, 12비트 수신값, LED 표시, 리셋

**원본과의 차이·연결 조건:** 원본의 명령 비트 배치를 유지하되 HIGH 대기 직렬 클록의 상승 에지에서 수신하도록 정리했다. sample은 수신 워드의 하위 12비트, led_out은 sample[11:4]다. 실제 ADC의 초기화와 채널 전환 시 변환 결과의 지연은 장치 설명서로 확인한다. TB는 디지털 직렬 응답만 모델링한다.


### 설계 모듈 · adc_command

> [!TIP]
> **설계 모듈 · adc_command**
>
> ```verilog
> `timescale 1ns/1ps
> module adc_command(input wire [2:0] channel,output wire [15:0] command);
>     // 원본 예제의 WR·SEQ·주소·전원·범위·코딩 비트 구성을 유지합니다.
>     assign command={3'b101,channel,2'b11,1'b0,3'b111,4'b0000};
> endmodule
>
> ```

### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module adc #(parameter HALF_CYCLES=25)(
>     input wire clk_50mhz,rst_p,
>     input wire [2:0] add_sel,
>     output wire adc_sclk,adc_ncs,adc_din,
>     input wire adc_dout,
>     output reg [11:0] sample,
>     output reg data_valid,
>     output wire [7:0] led_out
> );
>     wire [15:0] command,rx_word;
>     wire busy,done;
>     reg start;
>     adc_command u_command(add_sel,command);
>     serial_frame16 #(.HALF_CYCLES(HALF_CYCLES)) u_serial(
>         clk_50mhz,rst_p,start,command,adc_dout,
>         adc_sclk,adc_ncs,adc_din,busy,done,rx_word);
>     always @(posedge clk_50mhz) begin
>         if(rst_p) begin start<=0; sample<=0; data_valid<=0; end
>         else begin
>             start<=!busy && !start;
>             data_valid<=done;
>             if(done) sample<=rx_word[11:0];
>         end
>     end
>     assign led_out=sample[11:4];
> endmodule
>
> ```

### 설계 모듈 · serial_frame16

> [!TIP]
> **설계 모듈 · serial_frame16**
>
> ```verilog
> `timescale 1ns/1ps
> // 16비트 직렬 송수신. 클록은 HIGH 대기, 하강 에지에서 준비, 상승 에지에서 수신합니다.
> module serial_frame16 #(parameter HALF_CYCLES=25)(
>     input wire clk_50mhz,rst_p,start,
>     input wire [15:0] tx_word,
>     input wire miso,
>     output reg sclk,cs_n,mosi,busy,done,
>     output reg [15:0] rx_word
> );
>     reg [31:0] count;
>     reg [4:0] bit_index;
>     reg [15:0] tx_latched;
>     always @(posedge clk_50mhz) begin
>         if(rst_p) begin
>             sclk<=1; cs_n<=1; mosi<=0; busy<=0; done<=0;
>             count<=0; bit_index<=15; tx_latched<=0; rx_word<=0;
>         end else begin
>             done<=0;
>             if(!busy) begin
>                 if(start) begin
>                     cs_n<=0; busy<=1; count<=0; bit_index<=15;
>                     tx_latched<=tx_word; rx_word<=0; mosi<=tx_word[15];
>                 end
>             end else if(count==HALF_CYCLES-1) begin
>                 count<=0;
>                 if(sclk) begin sclk<=0; mosi<=tx_latched[bit_index]; end
>                 else begin
>                     sclk<=1;
>                     rx_word<={rx_word[14:0],miso};
>                     if(bit_index==0) begin busy<=0; cs_n<=1; done<=1; end
>                     else bit_index<=bit_index-1'b1;
>                 end
>             end else count<=count+1;
>         end
>     end
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg clk=0,rst=1;
>     always #5 clk=~clk;
>     reg [2:0] channel=2;
>     reg miso=0;
>     wire sclk,cs_n,mosi,valid;
>     wire [11:0] sample;
>     wire [7:0] led;
>     adc #(.HALF_CYCLES(2)) dut(clk,rst,channel,sclk,cs_n,mosi,miso,sample,valid,led);
>     reg [15:0] received_command;
>     reg [15:0] reply=16'hA5C3;
>     reg [2:0] frame_channel;
>     integer bit_no,received_bits,frames=0;
>     // ADC 모델: 하강 에지에서 응답 비트 준비, 상승 에지에서 명령 수신.
>     always @(negedge cs_n) begin
>         bit_no=15; received_bits=0; received_command=0; frame_channel=channel;
>     end
>     always @(negedge sclk)
>         if(!cs_n) miso=reply[bit_no];
>     always @(posedge sclk)
>         if(!rst && received_bits<16) begin
>             received_command={received_command[14:0],mosi};
>             received_bits=received_bits+1;
>             bit_no=bit_no-1;
>         end
>     always @(posedge valid) begin
>         #1;
>         if(received_bits != 16) $fatal(1,"ADC frame length");
>         if(received_command !== (16'hA370 | (frame_channel << 10)))
>             $fatal(1,"ADC command channel=%0d cmd=%h",frame_channel,received_command);
>         if(sample !== reply[11:0] || led !== reply[11:4]) $fatal(1,"ADC sample");
>         frames=frames+1;
>     end
>     initial begin
>         repeat(2) @(negedge clk);
>         if(cs_n!==1 || sclk!==1 || sample!==0) $fatal(1,"ADC reset");
>         rst=0;
>         wait(frames==1); @(negedge clk); channel=5;
>         wait(frames==2); @(negedge clk); channel=7;
>         wait(frames==3); @(negedge clk); rst=1;
>         @(posedge clk); #1;
>         if(cs_n!==1 || sclk!==1 || sample!==0 || valid!==0) $fatal(1,"ADC reset after data");
>         $display("PASS ADC: 3 serial frames, command bits, sample, reset"); $finish;
>     end
>     initial begin #100000; $fatal(1,"timeout"); end
> endmodule
>
> ```

## 8. DAC · STM32_2

**모듈 역할:** ramp8: 0~255 값 생성 / dac_parallel8: 데이터와 쓰기 펄스 / dac: 연결

**TB 검사:** 260회 쓰기와 255→0 전환, 채널 선택, 데이터 유지, 리셋

**원본과의 차이·연결 조건:** 기본 설정은 50 MHz에서 500000클록마다 쓰기 시작한다. 데이터는 LOW 쓰기 펄스 동안 유지하고, 펄스는 한 클록 길이다. 실제 DAC의 최소 쓰기 폭과 아날로그 출력은 장치 설명서와 계측으로 확인한다. TB는 디지털 입력 버스만 모델링한다.


### 설계 모듈 · dac_parallel8

> [!TIP]
> **설계 모듈 · dac_parallel8**
>
> ```verilog
> `timescale 1ns/1ps
> // 데이터는 쓰기 LOW 펄스 전에 등록하고, 펄스 종료까지 유지합니다.
> module dac_parallel8(
>     input wire clk_50mhz,rst_p,update,channel,
>     input wire [7:0] value,
>     output wire cs_n,ldac_n,
>     output reg we_n,a_b,
>     output reg [7:0] data
> );
>     assign cs_n=0;
>     assign ldac_n=0;
>     always @(posedge clk_50mhz) begin
>         if(rst_p) begin we_n<=1; a_b<=0; data<=0; end
>         else begin
>             we_n<=1;
>             if(update) begin data<=value; a_b<=channel; we_n<=0; end
>         end
>     end
> endmodule
>
> ```

### 설계 모듈 · 최상위 연결

> [!TIP]
> **설계 모듈 · 최상위 연결**
>
> ```verilog
> `timescale 1ns/1ps
> module dac #(parameter UPDATE_CYCLES=500_000)(
>     input wire clk_50mhz,rst_p,add_sel,
>     output wire dac_csn,dac_ldacn,dac_wen,dac_a_b,
>     output wire [7:0] dac_d,led_out
> );
>     wire [7:0] value;
>     wire update;
>     ramp8 #(.UPDATE_CYCLES(UPDATE_CYCLES)) u_ramp(clk_50mhz,rst_p,value,update);
>     dac_parallel8 u_bus(clk_50mhz,rst_p,update,add_sel,value,
>         dac_csn,dac_ldacn,dac_wen,dac_a_b,dac_d);
>     assign led_out=dac_d;
> endmodule
>
> ```

### 설계 모듈 · ramp8

> [!TIP]
> **설계 모듈 · ramp8**
>
> ```verilog
> `timescale 1ns/1ps
> module ramp8 #(parameter UPDATE_CYCLES=500_000)(
>     input wire clk_50mhz,rst_p,
>     output reg [7:0] value,
>     output wire update
> );
>     reg [31:0] count;
>     assign update=(count==UPDATE_CYCLES-1);
>     always @(posedge clk_50mhz) begin
>         if(rst_p) begin count<=0; value<=0; end
>         else if(update) begin count<=0; value<=value+1'b1; end
>         else count<=count+1;
>     end
> endmodule
>
> ```

### 테스트벤치

> [!TIP]
> **테스트벤치**
>
> ```systemverilog
> `timescale 1ns/1ps
> module tb;
>     reg clk=0,rst=1,channel=0;
>     always #5 clk=~clk;
>     wire cs_n,ldac_n,we_n,a_b;
>     wire [7:0] data,led;
>     dac #(.UPDATE_CYCLES(4)) dut(clk,rst,channel,cs_n,ldac_n,we_n,a_b,data,led);
>     integer writes=0;
>     time last_fall;
>     reg [7:0] held_data;
>     reg held_channel;
>     // 병렬 DAC 모델: LOW 펄스 동안 안정된 데이터를 종료 에지에서 기록합니다.
>     always @(negedge we_n) begin
>         #1; held_data=data; held_channel=a_b; last_fall=$time;
>     end
>     always @(posedge we_n) begin
>         if(!rst) begin
>             if($time-last_fall != 9) $fatal(1,"DAC write pulse width");
>             if(data !== held_data || a_b !== held_channel) $fatal(1,"DAC data hold");
>             if(data !== (writes%256) || led !== data) $fatal(1,"DAC ramp %0d",writes);
>             if(cs_n!==0 || ldac_n!==0 || a_b!==channel) $fatal(1,"DAC controls");
>             writes=writes+1;
>         end
>     end
>     initial begin
>         repeat(2) @(negedge clk); rst=0;
>         wait(writes==130); @(negedge clk); channel=1;
>         wait(writes==260); @(negedge clk); rst=1;
>         @(posedge clk); #1;
>         if(we_n!==1 || data!==0) $fatal(1,"DAC reset");
>         $display("PASS DAC: 260 writes, wraparound, channel, data hold, reset"); $finish;
>     end
>     initial begin #100000; $fatal(1,"timeout"); end
> endmodule
>
> ```
