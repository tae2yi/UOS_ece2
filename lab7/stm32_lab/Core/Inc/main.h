/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32g4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

void HAL_TIM_MspPostInit(TIM_HandleTypeDef *htim);

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define BUTTON_ece2_Pin GPIO_PIN_13
#define BUTTON_ece2_GPIO_Port GPIOC
#define BUTTON_ece2_EXTI_IRQn EXTI15_10_IRQn
#define GPIO_IN_PULLUP_ece2_Pin GPIO_PIN_0
#define GPIO_IN_PULLUP_ece2_GPIO_Port GPIOA
#define GPIO_IN_PULLUP_ece2_EXTI_IRQn EXTI0_IRQn
#define GPIO_IN_PULLDOWN_ece2_Pin GPIO_PIN_1
#define GPIO_IN_PULLDOWN_ece2_GPIO_Port GPIOA
#define GPIO_IN_PULLDOWN_ece2_EXTI_IRQn EXTI1_IRQn
#define UART_PC_TX_ece2_Pin GPIO_PIN_2
#define UART_PC_TX_ece2_GPIO_Port GPIOA
#define UART_PC_RX_ece2_Pin GPIO_PIN_3
#define UART_PC_RX_ece2_GPIO_Port GPIOA
#define LED_ece2_Pin GPIO_PIN_5
#define LED_ece2_GPIO_Port GPIOA
#define SPI_MISO_ece2_Pin GPIO_PIN_6
#define SPI_MISO_ece2_GPIO_Port GPIOA
#define SPI_MOSI_ece2_Pin GPIO_PIN_7
#define SPI_MOSI_ece2_GPIO_Port GPIOA
#define GPIO_OUT1_ece2_Pin GPIO_PIN_0
#define GPIO_OUT1_ece2_GPIO_Port GPIOB
#define GPIO_OUT2_ece2_Pin GPIO_PIN_1
#define GPIO_OUT2_ece2_GPIO_Port GPIOB
#define UART_FPGA_TX_ece2_Pin GPIO_PIN_10
#define UART_FPGA_TX_ece2_GPIO_Port GPIOC
#define UART_FPGA_RX_ece2_Pin GPIO_PIN_11
#define UART_FPGA_RX_ece2_GPIO_Port GPIOC
#define SPI_SCK_ece2_Pin GPIO_PIN_3
#define SPI_SCK_ece2_GPIO_Port GPIOB
#define PWM_OUT_ece2_Pin GPIO_PIN_4
#define PWM_OUT_ece2_GPIO_Port GPIOB
#define SPI_CS_ece2_Pin GPIO_PIN_6
#define SPI_CS_ece2_GPIO_Port GPIOB
#define I2C_SCL_ece2_Pin GPIO_PIN_8
#define I2C_SCL_ece2_GPIO_Port GPIOB
#define I2C_SDA_ece2_Pin GPIO_PIN_9
#define I2C_SDA_ece2_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
