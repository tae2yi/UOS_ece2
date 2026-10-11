/* PC에서 ece2_474_routine.c를 그대로 컴파일하기 위한 HAL 대역입니다.
 * 실습에 쓰는 GPIO·tick 함수만 흉내 내며 보드용 빌드에는 포함되지 않습니다.
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

typedef struct { int id; } TIM_TypeDef;
typedef struct { int id; } USART_TypeDef;
extern TIM_TypeDef hostsim_tim6;
extern USART_TypeDef hostsim_usart2, hostsim_usart3;
#define TIM6 (&hostsim_tim6)
#define USART2 (&hostsim_usart2)
#define USART3 (&hostsim_usart3)
typedef struct { TIM_TypeDef *Instance; } TIM_HandleTypeDef;
typedef struct { USART_TypeDef *Instance; } UART_HandleTypeDef;
typedef struct { int unused; } SPI_HandleTypeDef;
typedef struct { int unused; } I2C_HandleTypeDef;

uint32_t HAL_GetTick(void);
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *port, uint16_t pin);
void HAL_GPIO_WritePin(GPIO_TypeDef *port, uint16_t pin, GPIO_PinState state);
void HAL_GPIO_TogglePin(GPIO_TypeDef *port, uint16_t pin);
#endif
