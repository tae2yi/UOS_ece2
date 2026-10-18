/* 대비안: 뗄 때의 접점 떨림까지 거르는 버튼 처리 (호스트 시뮬레이션 전용 사본).
 * 과제 코드(lab5/stm32_lab/Core/Src/ece2_474_routine.c)와 다른 점만 있다.
 * - EXTI는 상승 에지만 알려 주므로, TIM6(100 ms)에서 버튼이 LOW인 것을 보면 armed = 1.
 * - button_isr_p7()은 armed일 때만 누름으로 인정하고 armed = 0으로 내린다.
 *   길게 누른 뒤 뗄 때의 떨림은 아직 TIM6가 LOW를 보기 전이라 무시된다.
 * - 과제4도 armed를 다시 세우려고 TIM6를 함께 시작한다.
 * STM32_1_TASK 3·4 선택은 과제 코드와 같다.
 */
#include "ece2_474.h"
#include "main.h"

#ifndef STM32_1_TASK
#define STM32_1_TASK 3
#endif
#define BUTTON_LOCK_MS 200U

#if STM32_1_TASK == 3
static volatile uint32_t blink_ticks = 10U;
#else
static volatile uint32_t pwm_compare = 250U;
#endif
static volatile uint8_t armed = 1U;

void ece2_474_init(void)
{
    HAL_TIM_Base_Start_IT(&htim6);
#if STM32_1_TASK == 4
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pwm_compare);
#endif
}

void polling_routine(void)
{
}

static void button_isr_p7(void)
{
    static uint32_t last_ms = 0;
    uint32_t now_ms = HAL_GetTick();
    if (!armed || now_ms - last_ms < BUTTON_LOCK_MS)
    {
        return;
    }
    armed = 0U;
    last_ms = now_ms;
#if STM32_1_TASK == 3
    blink_ticks = (blink_ticks >= 80U) ? 10U : blink_ticks * 2U;
#else
    pwm_compare = (pwm_compare >= 750U)
                  ? 250U : pwm_compare + 250U;
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, pwm_compare);
#endif
}

static void tim6_isr_p4(void)
{
    if (HAL_GPIO_ReadPin(BUTTON_ece2_GPIO_Port, BUTTON_ece2_Pin)
        == GPIO_PIN_RESET)
    {
        armed = 1U;
    }
#if STM32_1_TASK == 3
    static uint32_t count = 0;
    if (++count >= blink_ticks)
    {
        count = 0;
        HAL_GPIO_TogglePin(LED_ece2_GPIO_Port, LED_ece2_Pin);
    }
#endif
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    if (GPIO_Pin == BUTTON_ece2_Pin)
    {
        button_isr_p7();
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM6)
    {
        tim6_isr_p4();
    }
}
