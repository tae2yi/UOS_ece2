/* STM32_0 제공 예제 1 · 1초 간격 LED (docs/STM32_0.md의 코드 그대로) */
#include "ece2_474.h"
#include "main.h"

void ece2_474_init(void) {}

void polling_routine(void)
{
    static uint32_t last_ms = 0;
    static GPIO_PinState led_state = GPIO_PIN_RESET;
    uint32_t now_ms = HAL_GetTick();

    if (now_ms - last_ms >= 1000U)
    {
        last_ms = now_ms;
        led_state = (led_state == GPIO_PIN_RESET)
                    ? GPIO_PIN_SET : GPIO_PIN_RESET;
        HAL_GPIO_WritePin(LED_ece2_GPIO_Port, LED_ece2_Pin, led_state);
    }
}
