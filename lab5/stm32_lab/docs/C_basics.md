# 제공 코드에 나오는 C 문법

[실습 목차](index.md)

필요할 때 이 문서를 참고한다. 처음부터 모두 외울 필요는 없다.

## 변수와 자료형

변수는 값을 저장하는 공간이고, 자료형은 어떤 값을 저장하는지 정한다.

| 코드 | 뜻 | 실습에서 쓰는 예 |
|---|---|---|
| `int` | 정수 | getchar의 문자 값 또는 EOF |
| `uint8_t` | 0~255의 정수 | 통신할 한 바이트 |
| `uint16_t` | 0~65535의 정수 | 주소·핀 번호 |
| `uint32_t` | 0~4294967295의 정수 | 경과 시간·횟수 |
| `void` | 반환하는 값이 없음 | `void polling_routine(void)` |
| `GPIO_PinState` | 핀의 LOW/HIGH 상태를 나타내는 enum | 버튼 입력 |
| `HAL_StatusTypeDef` | 함수의 처리 결과를 나타내는 enum | 통신 성공 여부 |

`uint`는 음수가 없는 정수다. 숫자 8·16·32는 저장에 사용하는 비트 수다. `1000U`의 U는 음수 없는 정수 상수라는 표시다.

`void polling_routine(void)`는 입력으로 받는 값도, 돌려주는 값도 없는 함수다. `polling_routine();`은 그 함수를 실행하는 문장이다.

## enum · 이름을 붙인 정수 값

enum은 정수 값에 의미를 나타내는 이름을 붙인다. 상태를 코드에서 읽기 쉽게 표현할 때 사용한다.

> [!NOTE]
> **GPIO_PinState는 구조체가 아니라 enum이다.**
>
> HAL에 이미 다음과 같이 정의되어 있으므로 학생이 다시 작성하지 않는다.
>
> ```c
> typedef enum
> {
>     GPIO_PIN_RESET = 0,  /* LOW */
>     GPIO_PIN_SET       /* HIGH: 다음 값인 1 */
> } GPIO_PinState;
> ```
>
> `GPIO_PinState current;`는 핀 상태를 저장할 변수 current를 선언한다.

`typedef`는 자료형에 이름을 붙인다. 위 코드에서는 enum 자료형을 `GPIO_PinState`라는 이름으로 쓰도록 한다.

`HAL_StatusTypeDef`도 HAL에 정의된 enum이다.

| 이름 | 값 | 뜻 |
|---|---:|---|
| HAL_OK | 0 | 정상 완료 |
| HAL_ERROR | 1 | 오류 |
| HAL_BUSY | 2 | 사용 중 |
| HAL_TIMEOUT | 3 | 제한 시간 초과 |

예를 들어 `result == HAL_OK`는 결과가 정상인지 비교한다. enum 변수도 하나의 값을 저장한다.

## 구조체 · 여러 값을 묶은 자료형

구조체는 여러 변수를 하나로 묶는다. 예를 들어 학생의 학번과 점수를 함께 저장할 수 있다.

> [!NOTE]
> **문법 설명용 예제 · 실습 파일에 추가할 필요 없음**
>
> ```c
> typedef struct
> {
>     int number;
>     int score;
> } Student;
>
> Student student = {1, 90};
> ```
>
> Student는 자료형 이름이고 student는 변수 이름이다.
> `student.score`는 그 변수 안에 있는 score 값을 뜻한다.

STM32의 `UART_HandleTypeDef`, `TIM_HandleTypeDef`, `SPI_HandleTypeDef`, `I2C_HandleTypeDef`는 **구조체 자료형**이다. 어떤 주변장치를 쓰는지, 설정과 현재 상태가 무엇인지를 묶어 관리한다. 내부 전체를 외울 필요는 없다.

| 변수 | 자료형 | 담당 기능 |
|---|---|---|
| huart2 | UART_HandleTypeDef | 컴퓨터 통신 |
| huart3 | UART_HandleTypeDef | FPGA 통신 |
| htim6 | TIM_HandleTypeDef | 100 ms 타이머 |
| htim3 | TIM_HandleTypeDef | PWM |
| hspi1 | SPI_HandleTypeDef | SPI |
| hi2c1 | I2C_HandleTypeDef | I²C |

자료형 이름과 변수 이름은 다르다. `UART_HandleTypeDef huart3;`에서 앞쪽은 자료형, 뒤쪽은 변수다. 이 변수들은 이미 main.c에 정의되어 있다.

## extern · 다른 파일에 있는 변수 사용

`extern UART_HandleTypeDef huart3;`는 **다른 파일에 정의된 huart3를 여기에서도 사용하겠다**는 선언이다. 새 통신 장치를 만드는 코드가 아니다. 이번 템플릿은 주변장치 변수의 extern 선언을 ece2_474.h에 모아 두었다. 학생이 routine.c에 다시 선언할 필요는 없다.

`#include "ece2_474.h"`를 쓰면 헤더의 선언을 사용할 수 있다. 이 헤더는 자료형을 알 수 있도록 main.h도 포함한다.

main.c가 같은 헤더를 포함해도 충돌하지 않는다. 헤더의 extern은 변수의 존재를 알리는 **선언**이고, main.c의 `UART_HandleTypeDef huart3;`가 실제 저장 공간을 만드는 **정의**다. 선언과 정의의 자료형이 같으면 정상이다. 실제 변수 정의는 한 C 파일에만 둔다.

## &와 * · 주소와 포인터

`&huart3`는 huart3가 메모리에 저장된 **주소**다. HAL 함수는 이 주소를 받아 어떤 UART를 사용할지 확인한다.

`uint8_t data = 0x55;`에서 data는 값이고, `&data`는 그 값을 저장한 공간의 주소다. HAL 송수신 함수에 이 주소를 전달하면 해당 공간에서 데이터를 읽거나 저장한다.

> [!NOTE]
> `TIM_HandleTypeDef *htim`에서 *는 **주소를 저장하는 포인터 변수**라는 뜻이다.
>
> `htim->Instance`는 htim이 가리키는 구조체의 Instance 항목에 접근한다.
> 구조체 변수 자체는 `변수.항목`, 구조체 포인터는 `포인터->항목`으로 쓴다.
>
> 다른 위치의 *는 곱셈일 수 있다. 쓰인 위치에 따라 의미가 다르다.

## static · 다음 호출까지 값 보관

함수 안의 일반 변수는 함수가 실행될 때마다 만들어진다. `static` 변수는 함수가 끝나도 값을 유지한다.

`static uint32_t last_ms = 0;`은 처음에 한 번 0으로 초기화하고, 이후 호출에서도 마지막으로 저장한 시간을 유지한다. static 없이 매번 0으로 시작하면 마지막 실행 시간을 기억하지 못한다.

함수 앞의 `static`은 다른 뜻이다. `static void button_isr_p7(void)`는 **이 함수는 현재 C 파일 안에서만 사용한다**는 의미다.

## 조건문과 연산

| 코드 | 뜻 |
|---|---|
| `a = b;` | b의 값을 a에 저장 |
| `a == b` | 두 값이 같은지 비교 |
| `a != b` | 두 값이 다른지 비교 |
| `a >= b` | a가 b 이상인지 비교 |
| `조건1 && 조건2` | 두 조건이 모두 참 |
| `++count` | count를 1 증가시킨 뒤 그 값 사용 |
| `return;` | 현재 함수 실행을 끝냄 |
| `address << 1` | 비트를 왼쪽으로 한 칸 이동 |
| `(uint8_t)ch` | ch를 uint8_t 자료형으로 변환 |

`if (조건) { 코드 }`는 조건이 참일 때 중괄호 안을 실행한다.
`for (초기값; 반복 조건; 값 변경)`은 조건이 참인 동안 반복한다.

`HAL_GetTick()`은 시작 후 경과 시간을 ms 단위로 돌려준다. 1000 ms가 1초다. `now_ms - last_ms`는 마지막 동작 이후 지난 시간이다. 제공 코드에서는 음수 없는 정수의 뺄셈을 사용한다.

## 핀 이름과 출력 형식

`LED_ece2_Pin`, `BUTTON_ece2_Pin` 등은 main.h에 `#define`으로 정한 이름이다. 각각 LED 핀·버튼 핀 번호를 나타낸다. `LED_ece2_GPIO_Port`, `BUTTON_ece2_GPIO_Port`는 그 핀이 속한 GPIO 묶음이다. 구조체나 enum 자료형 이름이 아니다.

| printf 표기 | 표시할 값 |
|---|---|
| %c | 문자 한 개 |
| %d | int 정수를 십진수로 표시 |
| %02X | unsigned int 값을 대문자 16진수로, 최소 두 자리 표시 |
| `\r\n` | 출력에서 줄 바꾸기 |

`0x55`는 16진수로 쓴 숫자이며 십진수로는 85다.
`EOF`는 입력 종료나 실패를 나타내는 특별한 정수 값이다. 그래서 getchar의 결과는 uint8_t 대신 int로 받아 EOF인지 먼저 확인한다.
