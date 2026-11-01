#ifndef __ECE2_474_H
#define __ECE2_474_H

#include <stdio.h>
#include "main.h"

/* main.c에 정의된 주변장치 변수를 여러 파일에서 함께 사용합니다.
 * extern은 선언만 하므로, main.c에서 이 헤더를 포함해도 충돌하지 않습니다.
 */
extern TIM_HandleTypeDef htim6;
extern TIM_HandleTypeDef htim3;
extern UART_HandleTypeDef huart2;
extern UART_HandleTypeDef huart3;
extern SPI_HandleTypeDef hspi1;
extern I2C_HandleTypeDef hi2c1;

void ece2_474_init(void);
void polling_routine(void);


#endif /* __ECE2_474_H */