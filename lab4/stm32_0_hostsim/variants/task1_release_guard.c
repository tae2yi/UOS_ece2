/* STM32_0 과제1 대비안: 떼는 순간의 접점 떨림까지 막는 버튼 처리.
 * 보드에서 길게 눌렀다 뗄 때 간격이 두 번 바뀌면 ece2_474_routine.c의
 * polling_routine을 이 함수로 교체한다. 간격 처리 부분은 과제1 코드와 같다.
 */
#include "ece2_474.h"
#include "main.h"

void ece2_474_init(void) {}

void polling_routine(void)
{
    static GPIO_PinState previous = GPIO_PIN_RESET;
    static uint32_t last_change_ms = 0;
    static uint32_t last_toggle_ms = 0;
    static uint32_t interval_ms = 1000U;
    GPIO_PinState current =
        HAL_GPIO_ReadPin(BUTTON_ece2_GPIO_Port, BUTTON_ece2_Pin);
    uint32_t now_ms = HAL_GetTick();

    if (current != previous)
    {
        /* 직전 변화(누름·뗌 모두)에서 50 ms가 지난 뒤의 상승만 누름으로 인정한다. */
        if (current == GPIO_PIN_SET
            && now_ms - last_change_ms >= 50U)
        {
            interval_ms = (interval_ms >= 8000U)
                          ? 1000U : interval_ms * 2U;
        }
        last_change_ms = now_ms;
        previous = current;
    }

    if (now_ms - last_toggle_ms >= interval_ms)
    {
        last_toggle_ms = now_ms;
        HAL_GPIO_TogglePin(LED_ece2_GPIO_Port, LED_ece2_Pin);
    }
}
