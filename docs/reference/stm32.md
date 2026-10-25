# STM32 (NUCLEO-G474RE) 작업 요점

## 수업 프로젝트

- 조교 저장소 <https://github.com/Glaysia/ece2_474>, 태그 **v1.1.0**, 커밋 `dd94f01047aebdece09b9620c66e9b179403e5c9`. 4주 매뉴얼이 `docs/`에 전부 있다(매주 추가 매뉴얼 없음).
- 각 lab의 `labN/stm32_lab/`에 사본(중첩 `.git` 삭제). 학생이 고치는 파일은 **`Core/Src/ece2_474_routine.c` 하나**.
- 주차: STM32_0(10/12, 과제1·2 폴링 LED·버튼) / STM32_1(10/19, 과제3·4 버튼·TIM6 ISR, PWM) / STM32_2(10/26, 과제5~7 UART) / STM32_3(11/2, 과제8~12 SPI Mode 0, 8비트, MSB first, MISO 미사용).
- 매뉴얼의 "예제 시작과 전환": `ece2_474_init()`의 시작 호출 정리, 이전 동작 코드 비우기, 함수 선언과 `HAL_…Callback` 연결은 유지, Build 후 F5로 다운로드.
- 과제 여러 개는 매크로로 선택(lab4 `STM32_0_USE_EXTERNAL_LED`, lab6 `STM32_2_TASK=5|6`). 과제6·7은 같은 빌드.
- UART: 9600 8N1. PC–MCU = UART2(ST-LINK VCP), MCU–FPGA = UART3(PC10 TX).

## 이 PC에서 빌드

```bash
export PATH="/c/ece2/tools/arm-gnu-toolchain-13.3.rel1-mingw-w64-i686-arm-none-eabi/bin:/c/AMDDesignTools/2025.2/Vivado/tps/win64/cmake-3.24.2/bin:/c/AMDDesignTools/2025.2/Vivado/tps/mingw/10.0.0/win64.o/nt/bin:$PATH"
cd labN/stm32_lab && cmake --preset Debug && cmake --build --preset Debug
```
(lab4 기준 Flash 25,848 B, RAM 2,656 B.) 다른 과제 빌드는 `-DSTM32_2_TASK=6`처럼 캐시 변수를 더해 별도 폴더에. 출력은 `report/pre/logs/stm32_arm_build.txt`.

## 호스트 시뮬레이션 (보드 없이 사전 검증)

- `labN/stm32_K_hostsim/`: `mock/stm32g4xx_hal.h`(HAL 대역: GPIO, GetTick, TIM, UART Transmit 등) + `hostsim.c`(시나리오 구동, 50 µs 루프 스텝, CSV 출력).
- **보드용 routine.c를 수정 없이** PC gcc로 함께 컴파일한다. `bash run_hostsim.sh`(Windows는 Vivado MinGW gcc, 맥·리눅스는 `cc`).
- 시나리오: cycle / hold(길게 누름) / bounce(떨림) / wrap(틱 오버플로) / lock, UART는 PC 입력 바이트 파일 → VCP 출력 텍스트, UART3 바이트 hex(FPGA TB 입력).
- 보고서에는 "논리 검증일 뿐 실제 타이밍·배선은 보드에서 확인"이라고 적는다.

## 실습에서 있었던 일

- **디버그 모드 중단점**: 중단점에서 코어와 SysTick이 멈춰 `HAL_GetTick()`이 안 늘어 LED 간격이 길어 보인다(lab4 과제1: 4.80 s, 6.83 s → 정지 2.80·2.83 s 빼면 규칙과 일치. lab5 과제3: +1.47 s). ST-LINK LD1이 적·녹 깜빡이면 디버거 통신 중. 시간 측정 시에는 중단점 제거·디버거 없이 실행.
- PB0 외부 LED 위치는 CN7-34·A3로 적었지만 미확인(UM2505 대조 필요).
