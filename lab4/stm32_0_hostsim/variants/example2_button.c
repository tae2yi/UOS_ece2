/* STM32_0 제공 예제 2 · 버튼을 누르면 LED 변경 (docs/STM32_0.md의 코드 그대로) */
#include "ece2_474.h"
#include "main.h"

void ece2_474_init(void) {}

void polling_routine(void)
{
    static GPIO_PinState previous = GPIO_PIN_RESET;
    static uint32_t last_press_ms = 0;
    GPIO_PinState current = HAL_GPIO_ReadPin(BUTTON_ece2_GPIO_Port, BUTTON_ece2_Pin);
    uint32_t now_ms = HAL_GetTick();

    if (current == GPIO_PIN_SET && previous == GPIO_PIN_RESET
        && now_ms - last_press_ms >= 200U)
    {
        last_press_ms = now_ms;
        HAL_GPIO_TogglePin(LED_ece2_GPIO_Port, LED_ece2_Pin);
    }
    previous = current;
}
