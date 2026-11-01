/* PC에서 ece2_474_routine.c를 그대로 컴파일하기 위한 HAL 대역입니다.
 * 실습에 쓰는 GPIO·tick·SPI 함수만 흉내 내며 보드용 빌드에는 포함되지 않습니다.
 * (lab6/stm32_2_hostsim의 대역에 STM32_3의 SPI 송수신·재설정 함수를 더했다)
 */
#ifndef HOSTSIM_STM32G4XX_HAL_H
#define HOSTSIM_STM32G4XX_HAL_H
#include <stdint.h>

typedef enum { GPIO_PIN_RESET = 0, GPIO_PIN_SET } GPIO_PinState;
typedef struct { uint16_t idr, odr; char name; } GPIO_TypeDef;
extern GPIO_TypeDef hostsim_gpioa, hostsim_gpiob, hostsim_gpioc;
#define GPIOA (&hostsim_gpioa)
#define GPIOB (&hostsim_gpiob)
#define GPIOC (&hostsim_gpioc)
#define GPIO_PIN_0  ((uint16_t)0x0001)
#define GPIO_PIN_1  ((uint16_t)0x0002)
#define GPIO_PIN_2  ((uint16_t)0x0004)
#define GPIO_PIN_3  ((uint16_t)0x0008)
#define GPIO_PIN_4  ((uint16_t)0x0010)
#define GPIO_PIN_5  ((uint16_t)0x0020)
#define GPIO_PIN_6  ((uint16_t)0x0040)
#define GPIO_PIN_7  ((uint16_t)0x0080)
#define GPIO_PIN_8  ((uint16_t)0x0100)
#define GPIO_PIN_9  ((uint16_t)0x0200)
#define GPIO_PIN_10 ((uint16_t)0x0400)
#define GPIO_PIN_11 ((uint16_t)0x0800)
#define GPIO_PIN_13 ((uint16_t)0x2000)
typedef enum { EXTI0_IRQn = 6, EXTI1_IRQn = 7, EXTI15_10_IRQn = 40 } IRQn_Type;

/* GPIO 설정 구조체(슬레이브 NSS 핀 설정에 쓰인다). 값은 실제 HAL과 같은 이름만 맞췄다. */
typedef struct { uint32_t Pin, Mode, Pull, Speed, Alternate; } GPIO_InitTypeDef;
#define GPIO_MODE_AF_PP       0x00000002U
#define GPIO_PULLUP           0x00000001U
#define GPIO_SPEED_FREQ_LOW   0x00000000U
#define GPIO_AF5_SPI1         ((uint8_t)0x05)
void HAL_GPIO_Init(GPIO_TypeDef *port, GPIO_InitTypeDef *init);

typedef enum { HAL_OK = 0, HAL_ERROR = 1, HAL_BUSY = 2, HAL_TIMEOUT = 3 } HAL_StatusTypeDef;
typedef struct { int id; } TIM_TypeDef;
typedef struct { int id; } USART_TypeDef;
typedef struct { int id; } SPI_TypeDef;
extern TIM_TypeDef hostsim_tim6, hostsim_tim3;
extern USART_TypeDef hostsim_usart2, hostsim_usart3;
extern SPI_TypeDef hostsim_spi1;
#define TIM6 (&hostsim_tim6)
#define TIM3 (&hostsim_tim3)
#define USART2 (&hostsim_usart2)
#define USART3 (&hostsim_usart3)
#define SPI1 (&hostsim_spi1)
typedef struct { TIM_TypeDef *Instance; int running; uint32_t ccr1; } TIM_HandleTypeDef;
#define TIM_CHANNEL_1 0x00000000U
typedef struct { USART_TypeDef *Instance; } UART_HandleTypeDef;
typedef struct { int unused; } I2C_HandleTypeDef;

/* SPI: main.c의 MX_SPI1_Init 설정 항목 중 실습 코드가 바꾸는 Mode·NSS와 분주비를 둔다. */
#define SPI_MODE_MASTER          0x00000104U
#define SPI_MODE_SLAVE           0x00000000U
#define SPI_NSS_SOFT             0x00000200U
#define SPI_NSS_HARD_INPUT       0x00000000U
#define SPI_BAUDRATEPRESCALER_128 0x00000030U
typedef struct { uint32_t Mode, NSS, BaudRatePrescaler; } SPI_InitTypeDef;
typedef struct { SPI_TypeDef *Instance; SPI_InitTypeDef Init; int initialized; } SPI_HandleTypeDef;
HAL_StatusTypeDef HAL_SPI_Init(SPI_HandleTypeDef *hspi);
HAL_StatusTypeDef HAL_SPI_DeInit(SPI_HandleTypeDef *hspi);
HAL_StatusTypeDef HAL_SPI_Transmit(SPI_HandleTypeDef *hspi, const uint8_t *data,
                                   uint16_t size, uint32_t timeout);
HAL_StatusTypeDef HAL_SPI_Receive(SPI_HandleTypeDef *hspi, uint8_t *data,
                                  uint16_t size, uint32_t timeout);

uint32_t HAL_GetTick(void);
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *port, uint16_t pin);
void HAL_GPIO_WritePin(GPIO_TypeDef *port, uint16_t pin, GPIO_PinState state);
void HAL_GPIO_TogglePin(GPIO_TypeDef *port, uint16_t pin);

HAL_StatusTypeDef HAL_TIM_Base_Start_IT(TIM_HandleTypeDef *htim);
HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *htim, uint32_t channel);
void hostsim_set_compare(TIM_HandleTypeDef *htim, uint32_t channel, uint32_t value);
#define __HAL_TIM_SET_COMPARE(h, ch, v) hostsim_set_compare((h), (ch), (v))
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *huart, const uint8_t *data,
                                    uint16_t size, uint32_t timeout);

/* 실제 HAL에서는 각 주변장치 헤더에 선언된 콜백. 실습 파일이 정의한다. */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin);
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim);
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart);
#endif
