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

/* STM32_1 과제 선택. 3: 과제3(버튼·TIM6 ISR로 LED 간격 변경),
 * 4: 과제4(버튼으로 PWM 비율 변경). 둘은 따로 빌드해 확인합니다.
 */
#ifndef STM32_1_TASK
#define STM32_1_TASK 3
#endif

/* 버튼 ISR이 새 누름으로 인정하는 최소 간격(제공 예제와 같은 값) */
#define BUTTON_LOCK_MS 200U

#if STM32_1_TASK == 3
/* 과제3: LED 상태 변경 간격을 TIM6 호출 횟수로 저장(10 = 1초).
 * button_isr_p7()이 바꾸고 tim6_isr_p4()가 읽으므로 함수 밖에 둡니다.
 */
static volatile uint32_t blink_ticks = 10U;
#else
/* 과제4: TIM3 CH1 비교값. 한 주기가 1000칸이므로 250·500·750은
 * 25·50·75 %. 디버거의 Watch에서 이 변수를 봅니다.
 */
static volatile uint32_t pwm_compare = 250U;
#endif

/* 주변장치 초기화가 끝난 뒤, 메인 루프에 들어가기 전에 한 번 호출됩니다. */
void ece2_474_init(void)
{
    /* 필요한 기능만 주석을 해제합니다. 기본 핀·통신 설정은 이미 끝난 상태입니다.
     * VS Code에서 해당 줄에 커서를 놓거나 여러 줄을 선택하고 Ctrl + /를 누르면
     * 줄 주석(//)을 해제하거나 다시 설정할 수 있습니다.
     */

#if STM32_1_TASK == 3
    /* TIM6: 100 ms마다 tim6_isr_p4()를 호출합니다. */
    HAL_TIM_Base_Start_IT(&htim6);
#else
    /* TIM3: PB4에서 1 kHz PWM을 출력합니다. 과제4는 25 %에서 시작합니다. */
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pwm_compare);
#endif

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

/* 메인 루프에서 반복해서 호출됩니다.
 * STM32_1 과제3·4는 버튼과 LED·PWM을 모두 ISR에서 처리하므로 비워 둡니다.
 */
void polling_routine(void)
{
}

/* 1. 사용자 버튼 PC13을 눌렀을 때 호출됩니다. 우선순위: 7.
 * 버튼의 접점 때문에 한 번 눌러도 여러 번 호출될 수 있습니다.
 * 과제3은 간격을 1 -> 2 -> 4 -> 8 -> 1초, 과제4는 PWM 비율을
 * 25 -> 50 -> 75 -> 25 %로 한 단계씩 바꿉니다.
 */
static void button_isr_p7(void)
{
    static uint32_t last_ms = 0;
    uint32_t now_ms = HAL_GetTick();
    if (now_ms - last_ms < BUTTON_LOCK_MS)
    {
        return; /* 직전 누름 뒤 200 ms 안의 호출은 접점 떨림 */
    }
    last_ms = now_ms;
#if STM32_1_TASK == 3
    blink_ticks = (blink_ticks >= 80U) ? 10U : blink_ticks * 2U;
#else
    pwm_compare = (pwm_compare >= 750U)
                  ? 250U : pwm_compare + 250U;
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pwm_compare);
#endif
}

/* 2. TIM6를 인터럽트 방식으로 시작하면 100 ms마다 호출됩니다. 우선순위: 4.
 * 시작 호출: HAL_TIM_Base_Start_IT(&htim6);
 * 과제3: 호출 횟수가 blink_ticks에 이르면 내장 LED(PA5)를 바꿉니다.
 */
static void tim6_isr_p4(void)
{
#if STM32_1_TASK == 3
    static uint32_t count = 0;
    if (++count >= blink_ticks)
    {
        count = 0;
        HAL_GPIO_TogglePin(LED_ece2_GPIO_Port, LED_ece2_Pin);
    }
#endif
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
