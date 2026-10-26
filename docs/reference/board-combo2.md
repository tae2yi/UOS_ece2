# HBE-Combo II-DLD (Spartan-7 xc7s75fgga484-1) 핀과 장치

I/O 표준은 모두 LVCMOS33. 출처: 사용자가 찍어 준 장비 교재 사진(p.64~73, p.625, p.632, p.657~658), 이전 lab XDC, 실습장비 교재 PDF `HBE-Combo-II-DLD.pdf`(Ch.1 장비 이해, Ch.2 장치 1·2·3·4·7·10).
**사용자가 준 pinmap PDF는 같은 보드의 Spartan-6(XC6SLX45) 판이라 핀 번호가 전부 다르다 — 신호 이름 참고용으로만.**

## 확인된 핀

| 신호 | 핀 | 근거 |
|---|---|---|
| clk_50mhz (MAIN_CLOCK1) | **B6** | 클럭 제어 스위치로 0 Hz~50 MHz 16단계, **F = 50 MHz**인지 시연 전 확인 (표는 아래 "클럭 블록") |
| MAIN_CLOCK2/3/4 | C15 / P15 / M8 | 교재 |
| USER_CLOCK1/2 | D12 / U18 | 교재 |
| 리셋 버튼 SW1 | K4 | lab5·6 XDC |
| 버튼 SW2 / SW3 | N8 / N4 | 신호등 flicker / sw_flicker, lab6 서보 left/right |
| DIP_SW1~8 | Y1 W3 U2 T1 W4 W1 V4 U4 | LAB2 XDC (sw[7]..sw[0]) / LAB1 a[3]=Y1. 교재: **위로 올리면 1(High), 내리면 0** |
| LED1~8 | L4 M4 M2 N7 M7 M3 M1 N5 | p.625, 이전 lab |
| USB-UART TX / RX | F6 / C6 | LAB3-07, lab6 과제6은 RX를 BDIO로 옮김 |

### 신호등 모듈 (실습 37, p.657~658, EXT41~64) — 인덱스 3·2·1·0 = 남·북·서·동

| 신호 | 남 북 서 동 |
|---|---|
| red | B13 G14 C17 C12 |
| yellow | L18 A14 C18 D13 |
| green | E16 C16 A20 E11 |
| left | F15 D15 C19 F10 |
| walk_red | A19 G13 E18 C11 |
| walk_green | E19 F12 A16 G11 |

### ADC (실습 36, p.632): AD7908 8ch 8비트 SPI — ch0 CdS, ch1 가변저항
SPI_AD(CS) H3, SPI_DIN H5, SPI_DOUT J6, SPI_SCK H7. 채널 선택 DIP1·2·3 = add_sel[0..2].
칩은 SCLK 하강 에지에서 DIN을 읽고, CS 하강 때 첫 DOUT 비트를 낸다(lab5에서 문제 됨 → [../labs/lab5.md](../labs/lab5.md)).

### DAC (p.625 표): 8비트 병렬, CH0에 전압계
CSN E1, LDACN F4, WRN G4, A_B G2, D7..D0 = B3 B1 C4 C2 D5 D2 E5 E3. 같은 표의 clk=N8은 오타로 보임(메인 클록은 B6).

## 브레드보드 I/O (BDIO_0~15)

보드 위 브레드보드 바로 위 PORT A/B. PI3C3245 버스 스위치(3.3 V) + 100 Ω 직렬, **DIP SW5(BD_SEL1/2)를 켜야 연결**. 옆 헤더 J5 = BD_5V(퓨즈 350 mA), J6 = GND. 3.3 V 핀 없음.

BDIO 0 F8, 1 E8, 2 A7, 3 G8, 4 D7, 5 B7, 6 G7, 7 F7, 8 C8, 9 D8, 10 C9, 11 B8, 12 A9, 13 B9, 14 A10, 15 B10

lab6 과제6: MCU PC10(UART3 TX) → BDIO_0(F8), GND 공통.

## 확장 포트 EXT1~83

2×25 박스헤더 J18(EXT1~40), J19(EXT41~83), 각 선 33 Ω 직렬. J18 핀 n → EXT(n−4), J19 핀 n → EXT(n+36). 1~4번 근처 +5V, 45~50번 GND(배선 전 실물 확인). 기본으로 신호등 모듈이 꽂혀 있음.

EXT 1 G10, 2 C10, 3 F11, 4 D11, 5 A11, 6 E12, 7 A12, 8 F13, 9 C13, 10 A13, 11 F14, 12 B14, 13 G15, 14 E15, 15 B15, 16 D16, 17 B16, 18 E17, 19 A17, 20 D18,
21 A18, 22 D19, 23 B19, 24 B20, 25 A21, 26 B22, 27 C22, 28 D21, 29 F17, 30 F21, 31 G16, 32 G20, 33 G22, 34 H17, 35 H19, 36 H21, 37 J17, 38 J20, 39 J22, 40 K17,
41 F10, 42 G11, 43 E11, 44 C11, 45 F12, 46 C12, 47 G13, 48 D13, 49 B13, 50 G14, 51 L18, 52 A14, 53 F15, 54 D15, 55 E16, 56 C16, 57 A16, 58 C17, 59 E18, 60 C18,
61 E19, 62 C19, 63 A19, 64 A20, 65 B21, 66 C20, 67 D20, 68 E22, 69 F18, 70 F19, 71 F20, 72 F22, 73 G17, 74 G21, 75 H16, 76 H18, 77 H20, 78 J16, 79 J19, 80 J21,
81 K16, 82 K18, 83 K22

## 미확인 (사용자에게 교재 사진을 받아야 함 — 교재 PDF에도 없음)

- **서보 PWM 출력 핀** — lab6 XDC에 자리만 있음.

### SRAM K6R4016V1D 256K×16 (교재 p.603)
RAM_A0~A17 = L20 L22 M17 M18 N18 W22 V22 V20 V18 U20 V19 U22 U19 T21 T19 L19 L16 K19.
RAM_D0~D15 = P17 P21 R16 R18 R20 T17 T20 T22 T16 R19 R17 P22 P20 P16 N19 M16. RAM_CS N20, RAM_WE U17, RAM_OE L21 (모두 Low 활성).
/UB·/LB는 회로도에서 GND에 묶여 항상 16비트 동작. (사진은 페이지가 휘어 핀 값이 반 칸 위로 밀려 보임 — A17 = K19.)

## 내장 장치

8ch SPI ADC, DAC(8비트 병렬), 180° 서보(PWM), 스텝모터+자기센서, FND 4자리×2+1자리, 16×2 LCD, 버튼 12/키패드, DIP 8, LED 8, 풀컬러 LED, 피에조(5V), SRAM 4 Mbit, USB-UART, RS232. 베이스 336×273 mm.

## 교재 PDF(HBE-Combo-II-DLD) 보충

FPGA는 XC7S75 (로직셀 76,800, 임베디드 메모리 3,240 kbit, DSP 140, 구성 ROM 128 Mbit 플래시, JTAG+재구성 스위치). 베이스 보드 사양: SRAM 4 Mbit, FND 1자리 1개 + 4자리 2개(캐소드 공통), ADC 8ch SPI(CH0 VR, CH1 CdS), 확장 포트 2×25 헤더 2개(83 I/O), FPGA 92×102 mm / 베이스 336×273 mm.
(교재 사양표는 DAC를 "SPI 4ch"로 적었으나 위 DAC 핀(CSN/WRN/D0~7)은 병렬 — 핀 표를 따른다.)

### 클럭 블록
원형 스위치(0~F)로 BASE가 50 MHz를 분주해 MAIN_CLOCK으로 공급, 3자리 7-seg에 현재 값 표시.

| 스위치 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 주파수 | 0 | 1 Hz | 10 Hz | 50 Hz | 100 Hz | 500 Hz | 1 kHz | 5 kHz | 10 kHz | 50 kHz | 100 kHz | 500 kHz | 1 MHz | 5 MHz | 25 MHz | 50 MHz |

FPGA 모듈 자체 오실레이터는 USER_CLOCK1/2 (D12 / U18).

### 입력·LED 동작
- LED: FPGA 핀이 High면 켜짐. 미사용 핀은 툴 기본 풀업 때문에 희미하게 켜질 수 있다(장비 문제 아님).
- 버튼 12개: 누르면 High, 떼면 Low. 채터링 방지 회로 내장. **KEYPADS SEL 스위치를 아래로 내려야 버튼 스위치로 동작**(위로 올리면 3×4 키패드).
  SW_1~9 = K4 N8 N4 N1 P6 N6 L5 J2 K2, SW_* L7, SW_0 L1, SW_# K6.
- DIP 8개: 위로 올리면 1, 내리면 0 (고정형).

### 7-세그먼트 (캐소드 공통, 세그먼트 High = 점등)
1자리: SEG_A P1, B P3, C P7, D N3, E T5, F R2, G R4, DP R6.
디코더 {a,b,c,d,e,f,g}: 0=1111110, 1=0110000, 2=1101101, 3=1111001, 4=0110011, 5=1011011, 6=1011111, 7=1110000, 8=1111111, 9=1111011, A=1110111, b=0011111, C=1001110, d=0111101, E=1001111, F=1000111.

8자리 어레이는 세그먼트 데이터를 8자리가 공유하고 **자릿수 선택(common) 핀에 0을 준 자리만 켜지는 스캐닝 방식** — 한 자리씩 빠르게 돌려야 한다.
AR_SEG_A F1, B F5, C E2, D E4, E J1, F J3, G J7, DP H2. 자릿수 AR_SEG_S0~S7 = H4 H6 G1 G3 L6 K1 K3 K5.

### 피에조
PIEZO = **Y21**, 5 V 입력, PIEZO ENABLE 스위치를 켜야 소리. 1을 주는 것만으로는 안 되고 음높이에 해당하는 주파수의 펄스를 줘야 하며 약 10 kHz 이상은 들리지 않는다.
3옥타브(Hz): 도 261.6256, 레 293.6648, 미 329.6276, 파 349.2282, 솔 391.9954, 라 440, 시 493.8833 (2옥타브는 ½, 4옥타브는 2배).

### 16×2 텍스트 LCD
LCD_D0~D7 = A4 B2 C3 D4 A2 C5 C1 D1, LCD_RS G6, LCD_RW D6, LCD_E A6.
- 타이밍: E 주기 ≥500 ns, E High/Low ≥230 ns, RS/RW 셋업 ≥20 ns·홀드 ≥10 ns, 쓰기 데이터 셋업 ≥80 ns·홀드 ≥10 ns.
- 초기화: 전원 후 50 ms 이상 대기 → Function set(001x_xx00) → Display ON/OFF(00001DCB) → Entry mode(000001 I/D S) → DDRAM 주소 → 문자 연속 전송. 명령 사이는 충분히 기다리거나 busy flag(BF) 확인.
- 명령(RS RW DB7~0): Clear 00 0000_0001, Home 00 0000_001x, Entry 00 0000_01(I/D)S, Display 00 0000_1DCB, Shift 00 0001_(S/C)(R/L)xx, Function 00 001(IF)Nxxx (IF=1 8비트, N=1 2행), CGRAM 00 01+주소, DDRAM 00 1+주소, 데이터 쓰기 RS=1 RW=0.
- DDRAM 주소: 1행 0x00~0x0F, 2행 0x40~0x4F (연속 아님). 사용자 문자 CGRAM 최대 8개(전원 끄면 사라짐).
