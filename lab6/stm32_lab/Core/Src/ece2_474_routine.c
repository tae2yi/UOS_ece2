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

/* 주변장치 초기화가 끝난 뒤, 메인 루프에 들어가기 전에 한 번 호출됩니다. */
void ece2_474_init(void)
{
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

/* STM32_2 과제 선택: 5 = PC 입출력 확인,
 * 6 = 받은 바이트를 UART3로 FPGA에 전달(과제7도 같은 코드).
 * 과제6은 빌드할 때 -DSTM32_2_TASK=6을 준다.
 */
#ifndef STM32_2_TASK
#define STM32_2_TASK 5
#endif

/* 받은 바이트를 글자와 16진수 값으로 출력합니다.
 * 줄바꿈 문자는 \r, \n으로, 그 밖의 제어 문자와
 * 0x7F 이상(한글 UTF-8의 각 바이트 등)은 ?로 표시합니다.
 */
static void print_byte(uint8_t data)
{
    if (data == '\r')
    {
        printf("\\r");
    }
    else if (data == '\n')
    {
        printf("\\n");
    }
    else if (data < 0x20U || data > 0x7EU)
    {
        printf("?");
    }
    else
    {
        printf("%c", data);
    }
    printf(" (0x%02X)", data);
}

/* 메인 루프에서 반복해서 호출됩니다. */
void polling_routine(void)
{
    /* PC에서 문자가 올 때까지 getchar 안에서 기다립니다. */
    int ch = getchar();
    if (ch == EOF)
    {
        return;
    }
    uint8_t data = (uint8_t)ch;
#if STM32_2_TASK == 5
    printf("받은 문자: ");
    print_byte(data);
    printf("\r\n");
#else
    HAL_StatusTypeDef result =
        HAL_UART_Transmit(&huart3, &data, 1U, 100U);
    printf("FPGA로 보냄: ");
    print_byte(data);
    printf(", 전송 결과: %d\r\n", (int)result);
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
