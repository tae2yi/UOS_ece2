/*
 * 초기화·폴링·인터럽트 실습 템플릿입니다. CubeMX 자동 생성 파일이 아닙니다.
 * 학생은 아래 함수의 '실습 코드 작성' 부분을 채웁니다.
 * 아래쪽 HAL 콜백은 자동 생성된 인터럽트 처리 코드와 실습 함수를 연결합니다.
 * 인터럽트에서는 처리할 일을 기록하고 빠르게 돌아옵니다.
 * 인터럽트 함수 안에서는 HAL_Delay, scanf, getchar, printf를 사용하지 않습니다.
 */
#include "ece2_474.h"
#include "main.h"
/* 주변장치 변수의 extern 선언은 ece2_474.h에 있습니다. */

/* UART 인터럽트 수신 실습 때 필요한 버퍼의 주석을 해제합니다.
 * 파일 범위에 두면 수신 완료 함수에서도 같은 버퍼를 사용할 수 있습니다.
 */
// static uint8_t uart2_rx_ece2;
// static uint8_t uart3_rx_ece2;

/* STM32_3 역할 선택 (SPI Mode 0, 8비트, MSB first, MISO 미사용)
 * 1 = SPI1 마스터 송신: 과제8(파형), 과제9 송신 측, 과제10(MCU -> FPGA)
 * 2 = SPI1 슬레이브 수신: 과제9 수신 측, 과제11(FPGA -> MCU)
 * 수신 측은 빌드할 때 -DSTM32_3_ROLE=2를 준다(또는 아래 기본값을 2로 바꾼다).
 */
#ifndef STM32_3_ROLE
#define STM32_3_ROLE 1
#endif

/* 마스터가 보낼 값. 기본은 매뉴얼의 네 값을 1초마다 차례로 보낸다.
 * 오실로스코프에서 한 값만 계속 보려면 -DSTM32_3_TX_FIXED=0x55처럼 준다.
 */
#if STM32_3_ROLE == 1 && !defined(STM32_3_TX_FIXED)
static const uint8_t tx_values_ece2[] = {0x55U, 0xA5U, 0x00U, 0xFFU};
#endif

/* 수신 측 장치 선택 입력: PA4 = SPI1 NSS (송신 측 CS는 PB6) */
#define SPI_NSS_RX_ece2_Pin       GPIO_PIN_4
#define SPI_NSS_RX_ece2_GPIO_Port GPIOA

/* 주변장치 초기화가 끝난 뒤, 메인 루프에 들어가기 전에 한 번 호출됩니다. */
void ece2_474_init(void)
{
#if STM32_3_ROLE == 2
    /* 수신: main.c는 그대로, SPI1만 슬레이브로 재설정 */
    if (HAL_SPI_DeInit(&hspi1) != HAL_OK)
        Error_Handler();

    hspi1.Init.Mode = SPI_MODE_SLAVE;
    hspi1.Init.NSS = SPI_NSS_HARD_INPUT;
    if (HAL_SPI_Init(&hspi1) != HAL_OK)
        Error_Handler();

    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = SPI_NSS_RX_ece2_Pin;
    gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_PULLUP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    gpio.Alternate = GPIO_AF5_SPI1;
    HAL_GPIO_Init(SPI_NSS_RX_ece2_GPIO_Port, &gpio);
#endif

    /* 필요한 기능만 주석을 해제합니다. 기본 핀·통신 설정은 이미 끝난 상태입니다.
     * VS Code에서 해당 줄에 커서를 놓거나 여러 줄을 선택하고 Ctrl + /를 누르면
     * 줄 주석(//)을 해제하거나 다시 설정할 수 있습니다.
     */

    /* TIM6: 100 ms마다 tim6_isr_p4()를 호출합니다. */
    // HAL_TIM_Base_Start_IT(&htim6);

    /* TIM3: PB4에서 1 kHz PWM을 출력합니다. 비교값 500은 50%입니다. */
    // HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    // __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, 500U);

    /* UART2: PC에서 한 바이트를 받으면 uart2_isr_p6()를 호출합니다.
     * 위의 uart2_rx_ece2 버퍼도 주석을 해제해야 합니다.
     * 수신 완료 함수에서 HAL_UART_Receive_IT를 다시 호출해야 다음 입력도 받습니다.
     * getchar·fgets·scanf로 같은 UART를 읽는 방식과 함께 사용하지 않습니다.
     */
    // HAL_UART_Receive_IT(&huart2, &uart2_rx_ece2, 1U);

    /* UART3: FPGA에서 한 바이트를 받으면 uart3_isr_p5()를 호출합니다.
     * 위의 uart3_rx_ece2 버퍼도 주석을 해제해야 합니다.
     * UART는 한 번 수신한 뒤, 수신 완료 함수에서 다시 수신을 요청합니다.
     */
    // HAL_UART_Receive_IT(&huart3, &uart3_rx_ece2, 1U);

    /* GPIO 입력 인터럽트는 이미 켜져 있어 별도 시작 호출이 필요 없습니다.
     * SPI·I2C와 UART 송신도 별도 시작 없이 필요한 시점에 송수신 함수를 호출합니다.
     */
}

/* 메인 루프에서 반복해서 호출됩니다. */
void polling_routine(void)
{
#if STM32_3_ROLE == 1
    /* 송신: 1초마다 CS LOW, 1바이트, CS HIGH */
    static uint32_t last_ms = 0;
    static uint32_t index = 0;
    uint32_t now_ms = HAL_GetTick();
    if (now_ms - last_ms < 1000U) return;
    last_ms = now_ms;

#ifdef STM32_3_TX_FIXED
    uint8_t tx = (uint8_t)(STM32_3_TX_FIXED);
    (void)index;
#else
    uint8_t tx = tx_values_ece2[index];
    index = (index + 1U) %
            (sizeof(tx_values_ece2) / sizeof(tx_values_ece2[0]));
#endif
    HAL_GPIO_WritePin(SPI_CS_ece2_GPIO_Port,
                      SPI_CS_ece2_Pin, GPIO_PIN_RESET);
    HAL_StatusTypeDef result =
        HAL_SPI_Transmit(&hspi1, &tx, 1U, 100U);
    HAL_GPIO_WritePin(SPI_CS_ece2_GPIO_Port,
                      SPI_CS_ece2_Pin, GPIO_PIN_SET);

    printf("TX=%02X, result=%d\r\n",
           (unsigned int)tx, (int)result);
#else
    /* 수신: 최대 2초 기다려 결과를 VCP로 출력 */
    uint8_t rx = 0;
    HAL_StatusTypeDef result =
        HAL_SPI_Receive(&hspi1, &rx, 1U, 2000U);
    if (result == HAL_OK)
    {
        printf("RX=%02X\r\n", (unsigned int)rx);
    }
    else if (result == HAL_TIMEOUT)
    {
        /* 매뉴얼 한 줄을 둘로 나눔(같은 문자열) */
        printf("RX timeout: check sender, SCK, MOSI, "
               "CS and GND\r\n");
    }
    else
    {
        printf("RX error=%d\r\n", (int)result);
    }
#endif
}

/* 1. 사용자 버튼 PC13을 눌렀을 때 호출됩니다. 우선순위: 7.
 * 버튼의 접점 때문에 한 번 눌러도 여러 번 호출될 수 있습니다.
 */
static void button_isr_p7(void)
{
    /* 실습 코드 작성: 버튼 이벤트를 기록하거나 LED 상태를 변경합니다. */
}

/* 2. TIM6를 인터럽트 방식으로 시작하면 100 ms마다 호출됩니다. 우선순위: 4.
 * 시작 호출: HAL_TIM_Base_Start_IT(&htim6);
 */
static void tim6_isr_p4(void)
{
    /* 실습 코드 작성: 횟수를 세거나 메인 루프에서 처리할 표시를 남깁니다. */
}

/* 3. PC 통신 UART2의 요청한 수신이 완료되면 호출됩니다. 우선순위: 6.
 * 먼저 수신 버퍼를 준비하고 HAL_UART_Receive_IT로 수신을 요청해야 합니다.
 * 다음 입력도 받으려면 처리 후 수신을 다시 요청합니다.
 * 현재 표준 입력은 기다리는 방식입니다. 같은 UART의 인터럽트 수신과 함께 쓰지 않습니다.
 */
static void uart2_isr_p6(void)
{
    /* 실습 코드 작성: PC 수신 버퍼를 처리하고 다음 수신을 요청합니다. */
}

/* 4. FPGA 통신 UART3의 요청한 수신이 완료되면 호출됩니다. 우선순위: 5.
 * 먼저 수신 버퍼를 준비하고 HAL_UART_Receive_IT로 수신을 요청해야 합니다.
 * 다음 입력도 받으려면 처리 후 수신을 다시 요청합니다.
 */
static void uart3_isr_p5(void)
{
    /* 실습 코드 작성: FPGA 수신 버퍼를 처리하고 다음 수신을 요청합니다. */
}

/* PA0: 풀업 입력의 HIGH -> LOW 변화. 우선순위: 8. */
static void gpio_in_pullup_isr_p8_ece2(void)
{
    /* 실습 코드 작성 */
}

/* PA1: 풀다운 입력의 LOW -> HIGH 변화. 우선순위: 9. */
static void gpio_in_pulldown_isr_p9_ece2(void)
{
    /* 실습 코드 작성 */
}

/* 아래는 HAL 콜백과 실습 함수를 연결하는 코드입니다. */

/* CubeMX의 EXTI 처리 코드에서 버튼 실습 함수로 연결합니다. */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == BUTTON_ece2_Pin)
    {
        button_isr_p7();
    }
    else if (GPIO_Pin == GPIO_IN_PULLUP_ece2_Pin)
    {
        gpio_in_pullup_isr_p8_ece2();
    }
    else if (GPIO_Pin == GPIO_IN_PULLDOWN_ece2_Pin)
    {
        gpio_in_pulldown_isr_p9_ece2();
    }
}

/* CubeMX의 타이머 처리 코드에서 TIM6 실습 함수로 연결합니다. */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM6)
    {
        tim6_isr_p4();
    }
}

/* UART 수신 완료 시 PC 통신과 FPGA 통신을 구분합니다. */
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2)
    {
        uart2_isr_p6();
    }
    else if (huart->Instance == USART3)
    {
        uart3_isr_p5();
    }
}
