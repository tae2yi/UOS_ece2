# HBE-Combo II-DLD (Spartan-7 xc7s75fgga484-1) 핀과 장치

I/O 표준은 모두 LVCMOS33. 출처: 사용자가 찍어 준 장비 교재 사진(p.64~73, p.625, p.632, p.657~658), 이전 lab XDC.
**사용자가 준 pinmap PDF는 같은 보드의 Spartan-6(XC6SLX45) 판이라 핀 번호가 전부 다르다 — 신호 이름 참고용으로만.**

## 확인된 핀

| 신호 | 핀 | 근거 |
|---|---|---|
| clk_50mhz (MAIN_CLOCK1) | **B6** | 클럭 제어 스위치로 0 Hz~50 MHz 16단계, **F = 50 MHz**인지 시연 전 확인 |
| MAIN_CLOCK2/3/4 | C15 / P15 / M8 | 교재 |
| USER_CLOCK1/2 | D12 / U18 | 교재 |
| 리셋 버튼 SW1 | K4 | lab5·6 XDC |
| 버튼 SW2 / SW3 | N8 / N4 | 신호등 flicker / sw_flicker, lab6 서보 left/right |
| DIP_SW1~8 | Y1 W3 U2 T1 W4 W1 V4 U4 | LAB2 XDC (sw[7]..sw[0]) / LAB1 a[3]=Y1. **어느 방향이 1인지 미확인** |
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

## 미확인 (사용자에게 교재 사진을 받아야 함)

- **서보 PWM 출력 핀**, **SRAM 버스 핀**(주소·데이터·/CS·/OE·/WE, /UB·/LB 연결 여부) — lab6 XDC에 자리만 있음.

## 내장 장치

8ch SPI ADC, DAC(8비트 병렬), 180° 서보(PWM), 스텝모터+자기센서, FND 4자리×2+1자리, 16×2 LCD, 버튼 12/키패드, DIP 8, LED 8, 풀컬러 LED, 피에조(5V), SRAM 4 Mbit, USB-UART, RS232. 베이스 336×273 mm.
