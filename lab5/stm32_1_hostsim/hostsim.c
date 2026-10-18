/* STM32_1 호스트 시뮬레이션.
 * 보드에 올릴 ece2_474_routine.c를 PC에서 그대로 컴파일하고, 인터럽트가 하던 일을 대신 호출한다.
 * - SysTick: 1 ms마다 HAL_GetTick() 값이 1 늘어난다.
 * - TIM6: HAL_TIM_Base_Start_IT로 시작했으면 100 ms마다 HAL_TIM_PeriodElapsedCallback(&htim6).
 * - EXTI: PC13 버튼 값이 LOW -> HIGH로 바뀔 때마다 HAL_GPIO_EXTI_Callback(BUTTON_ece2_Pin).
 *   (CubeMX 설정이 상승 에지 인터럽트다. 떨림이 있으면 상승 에지마다 호출된다.)
 * - 메인 루프: 시간 단위(STEP_US = 50 us)마다 polling_routine()을 한 번 호출한다.
 * 같은 시각에 두 인터럽트가 겹치면 우선순위가 높은 TIM6(4)를 버튼(7)보다 먼저 처리한다.
 * 버튼은 시나리오 표의 누름·뗌 시각과 접점 떨림(에지마다 bounce_n번, 한 번에 BOUNCE_US) 모델로 만든다.
 * 출력: 표준 출력에 "시각(ms),신호,값" CSV. 실제 보드 측정이 아니라 논리 검증용이다.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ece2_474.h"
#include "main.h"

#define STEP_US 50ULL
#define BOUNCE_US 400ULL
#define TIM6_PERIOD_US 100000ULL

GPIO_TypeDef hostsim_gpioa = {0, 0, 'A'}, hostsim_gpiob = {0, 0, 'B'}, hostsim_gpioc = {0, 0, 'C'};
TIM_TypeDef hostsim_tim6, hostsim_tim3;
USART_TypeDef hostsim_usart2, hostsim_usart3;
TIM_HandleTypeDef htim6 = {TIM6, 0, 0}, htim3 = {TIM3, 0, 500U};
UART_HandleTypeDef huart2, huart3;
SPI_HandleTypeDef hspi1;
I2C_HandleTypeDef hi2c1;

static unsigned long long t_us;

static void log_event(const char *signal, long value)
{
    printf("%llu.%03llu,%s,%ld\n", t_us / 1000ULL, t_us % 1000ULL, signal, value);
}

uint32_t HAL_GetTick(void) { return (uint32_t)(t_us / 1000ULL); }

GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *port, uint16_t pin)
{
    return (port->idr & pin) ? GPIO_PIN_SET : GPIO_PIN_RESET;
}

static void write_odr(GPIO_TypeDef *port, uint16_t odr)
{
    uint16_t changed = port->odr ^ odr;
    port->odr = odr;
    for (int bit = 0; bit < 16; bit++)
        if (changed & (1U << bit))
        {
            char name[8];
            snprintf(name, sizeof name, "P%c%d", port->name, bit);
            log_event(name, (odr >> bit) & 1);
        }
}

void HAL_GPIO_WritePin(GPIO_TypeDef *port, uint16_t pin, GPIO_PinState state)
{
    write_odr(port, state == GPIO_PIN_SET ? (port->odr | pin) : (port->odr & (uint16_t)~pin));
}

void HAL_GPIO_TogglePin(GPIO_TypeDef *port, uint16_t pin) { write_odr(port, port->odr ^ pin); }

HAL_StatusTypeDef HAL_TIM_Base_Start_IT(TIM_HandleTypeDef *htim)
{
    htim->running = 1;
    log_event(htim->Instance == TIM6 ? "TIM6_START" : "TIM_START", 1);
    return HAL_OK;
}

HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *htim, uint32_t channel)
{
    (void)channel;
    htim->running = 1;
    log_event("PWM_START", 1);
    log_event("CCR1", (long)htim->ccr1);
    return HAL_OK;
}

void hostsim_set_compare(TIM_HandleTypeDef *htim, uint32_t channel, uint32_t value)
{
    (void)channel;
    htim->ccr1 = value;
    log_event("CCR1", (long)value);
}

typedef struct { unsigned long long press_us, release_us; } press_t;
typedef struct
{
    const char *name;
    unsigned long long end_us;
    int bounce_n;
    int count;
    press_t press[8];
} scenario_t;

#define MS(x) ((unsigned long long)(x) * 1000ULL)
static const scenario_t scenarios[] = {
    /* 과제3: 짧게 네 번. 1 -> 2 -> 4 -> 8 -> 1초 순환 */
    {"cycle", MS(52500), 0, 4,
     {{MS(4550), MS(4700)}, {MS(10550), MS(10700)}, {MS(22550), MS(22700)}, {MS(46550), MS(46700)}}},
    /* 6초 동안 계속 누름: 상승 에지가 한 번뿐이라 한 번만 바뀌어야 함 */
    {"hold", MS(12500), 0, 1, {{MS(2550), MS(8550)}}},
    /* 접점 떨림: 짧은 누름 한 번, 1.5초 누름 한 번 */
    {"bounce", MS(20500), 5, 2, {{MS(2550), MS(2700)}, {MS(6550), MS(8050)}}},
    /* 200 ms 잠금: 150 ms 간격 두 번(두 번째 무시), 300 ms 간격 두 번(둘 다 인정) */
    {"lock", MS(10500), 0, 4,
     {{MS(2550), MS(2600)}, {MS(2700), MS(2750)}, {MS(5550), MS(5600)}, {MS(5850), MS(5900)}}},
    /* 과제4: 1초마다 짧게 네 번. 25 -> 50 -> 75 -> 25 -> 50 % */
    {"pwm", MS(5000), 0, 4,
     {{MS(1050), MS(1200)}, {MS(2050), MS(2200)}, {MS(3050), MS(3200)}, {MS(4050), MS(4200)}}},
    /* 과제4 떨림: 짧은 누름 한 번, 1.5초 누름 한 번 */
    {"pwm_bounce", MS(5000), 5, 2, {{MS(1050), MS(1200)}, {MS(2050), MS(3550)}}},
};

/* 에지 뒤 BOUNCE_US마다 값이 뒤집히다가 bounce_n번 뒤 새 값으로 안정된다. */
static int button_level(const scenario_t *s, unsigned long long t)
{
    int level = 0;
    for (int i = 0; i < s->count; i++)
    {
        unsigned long long edge[2] = {s->press[i].press_us, s->press[i].release_us};
        for (int e = 0; e < 2; e++)
        {
            int target = (e == 0);
            if (t < edge[e]) continue;
            unsigned long long k = (t - edge[e]) / BOUNCE_US;
            level = (k < (unsigned long long)(2 * s->bounce_n) && (k & 1ULL)) ? !target : target;
        }
    }
    return level;
}

int main(int argc, char **argv)
{
    const scenario_t *s = NULL;
    for (size_t i = 0; argc > 1 && i < sizeof scenarios / sizeof scenarios[0]; i++)
        if (strcmp(argv[1], scenarios[i].name) == 0) s = &scenarios[i];
    if (!s)
    {
        fprintf(stderr, "usage: hostsim cycle|hold|bounce|lock|pwm|pwm_bounce\n");
        return 2;
    }

    int shown = 0;
    long exti_calls = 0;
    log_event("BUTTON", 0);
    ece2_474_init();
    for (t_us = 0; t_us <= s->end_us; t_us += STEP_US)
    {
        if (htim6.running && t_us > 0 && t_us % TIM6_PERIOD_US == 0)
            HAL_TIM_PeriodElapsedCallback(&htim6);

        int level = button_level(s, t_us);
        hostsim_gpioc.idr = level ? BUTTON_ece2_Pin : 0;
        if (level != shown)
        {
            log_event("BUTTON", level);
            if (level)
            {
                log_event("EXTI", ++exti_calls);
                HAL_GPIO_EXTI_Callback(BUTTON_ece2_Pin);
            }
            shown = level;
        }
        polling_routine();
    }
    t_us = s->end_us;
    log_event("END", 0);
    return 0;
}
