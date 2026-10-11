/* STM32_0 호스트 시뮬레이션.
 * 보드에 올릴 polling_routine()을 PC에서 그대로 호출하며, HAL_GetTick과 GPIO만 흉내 낸다.
 * 메인 루프 한 바퀴를 STEP_US(50 us)로 두고, 버튼은 시나리오 표의 누름·뗌 시각과
 * 접점 떨림(에지마다 bounce_n번, 한 번에 BOUNCE_US) 모델로 만든다.
 * 출력: 표준 출력에 "시각(ms),신호,값" CSV. 실제 보드 측정이 아니라 논리 검증용이다.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ece2_474.h"
#include "main.h"

#define STEP_US 50ULL
#define BOUNCE_US 400ULL

GPIO_TypeDef hostsim_gpioa = {0, 0, 'A'}, hostsim_gpiob = {0, 0, 'B'}, hostsim_gpioc = {0, 0, 'C'};
TIM_TypeDef hostsim_tim6;
USART_TypeDef hostsim_usart2, hostsim_usart3;
TIM_HandleTypeDef htim6, htim3;
UART_HandleTypeDef huart2, huart3;
SPI_HandleTypeDef hspi1;
I2C_HandleTypeDef hi2c1;

static unsigned long long t_us;
static uint32_t tick_offset;

static void log_event(const char *signal, int value)
{
    printf("%llu.%03llu,%s,%d\n", t_us / 1000ULL, t_us % 1000ULL, signal, value);
}

uint32_t HAL_GetTick(void) { return tick_offset + (uint32_t)(t_us / 1000ULL); }

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

typedef struct { unsigned long long press_us, release_us; } press_t;
typedef struct
{
    const char *name;
    unsigned long long end_us;
    int bounce_n;
    uint32_t tick0;
    int count;
    press_t press[8];
} scenario_t;

#define MS(x) ((unsigned long long)(x) * 1000ULL)
static const scenario_t scenarios[] = {
    /* 짧게 네 번: 1 -> 2 -> 4 -> 8 -> 1초 순환 */
    {"cycle", MS(52500), 0, 0, 4,
     {{MS(4500), MS(4650)}, {MS(10500), MS(10650)}, {MS(22500), MS(22650)}, {MS(46500), MS(46650)}}},
    /* 6초 동안 계속 누름: 한 번만 바뀌어야 함 */
    {"hold", MS(12500), 0, 0, 1, {{MS(2500), MS(8500)}}},
    /* 접점 떨림: 짧은 누름 한 번, 1.5초 누름 한 번 */
    {"bounce", MS(20500), 5, 0, 2, {{MS(2500), MS(2650)}, {MS(6500), MS(8000)}}},
    /* cycle과 같은 입력을 tick이 0xFFFFFFFF를 넘어가는 구간에서 실행 */
    {"wrap", MS(52500), 0, 0xFFFFFFFFU - 20000U + 1U, 4,
     {{MS(4500), MS(4650)}, {MS(10500), MS(10650)}, {MS(22500), MS(22650)}, {MS(46500), MS(46650)}}},
    /* 짧게 세 번: 제공 예제 2 확인용 */
    {"taps", MS(8500), 0, 0, 3, {{MS(1500), MS(1650)}, {MS(3500), MS(3650)}, {MS(5500), MS(7000)}}},
    /* 입력 없음 */
    {"idle", MS(5500), 0, 0, 0, {{0, 0}}},
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
        fprintf(stderr, "usage: hostsim cycle|hold|bounce|wrap|taps|idle\n");
        return 2;
    }

    tick_offset = s->tick0;
    int shown = -1;
    ece2_474_init();
    for (t_us = 0; t_us <= s->end_us; t_us += STEP_US)
    {
        int level = button_level(s, t_us);
        if (level != shown) { log_event("BUTTON", level); shown = level; }
        hostsim_gpioc.idr = level ? BUTTON_ece2_Pin : 0;
        polling_routine();
    }
    t_us = s->end_us;
    log_event("END", 0);
    return 0;
}
