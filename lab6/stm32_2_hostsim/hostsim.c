/* STM32_2 호스트 시뮬레이션.
 * 보드에 올릴 ece2_474_routine.c를 PC에서 그대로 컴파일하고 polling_routine()을 반복 호출한다.
 * - PC → MCU(UART2): 표준 입력의 바이트를 getchar()가 그대로 읽는다(Serial Monitor의 보내기 대신).
 *   입력이 끝나면(EOF) 시뮬레이션을 마친다. 보드의 getchar는 EOF 없이 계속 기다린다.
 * - MCU → PC(UART2): printf 출력이 표준 출력으로 나온다(Serial Monitor 화면 대신).
 * - MCU → FPGA(UART3): HAL_UART_Transmit(&huart3, ...)로 보낸 바이트를 argv[1] 파일에
 *   한 줄에 한 바이트씩 16진수로 적는다. FPGA 테스트벤치가 $readmemh로 읽어 직렬 신호로 만든다.
 * 실제 보드 측정이 아니라 실습 코드의 판단과 출력 형식을 확인하는 논리 검증용이다.
 */
#include <stdio.h>
#include <stdlib.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#include "ece2_474.h"
#include "main.h"

GPIO_TypeDef hostsim_gpioa = {0, 0, 'A'}, hostsim_gpiob = {0, 0, 'B'}, hostsim_gpioc = {0, 0, 'C'};
TIM_TypeDef hostsim_tim6, hostsim_tim3;
USART_TypeDef hostsim_usart2, hostsim_usart3;
TIM_HandleTypeDef htim6 = {TIM6, 0, 0}, htim3 = {TIM3, 0, 500U};
UART_HandleTypeDef huart2 = {USART2}, huart3 = {USART3};
SPI_HandleTypeDef hspi1;
I2C_HandleTypeDef hi2c1;

static FILE *uart3_out;
static int uart3_count;

uint32_t HAL_GetTick(void) { return 0U; }
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *port, uint16_t pin)
{
    return (port->idr & pin) ? GPIO_PIN_SET : GPIO_PIN_RESET;
}
void HAL_GPIO_WritePin(GPIO_TypeDef *port, uint16_t pin, GPIO_PinState state)
{
    port->odr = state == GPIO_PIN_SET ? (port->odr | pin) : (port->odr & (uint16_t)~pin);
}
void HAL_GPIO_TogglePin(GPIO_TypeDef *port, uint16_t pin) { port->odr ^= pin; }
HAL_StatusTypeDef HAL_TIM_Base_Start_IT(TIM_HandleTypeDef *htim) { htim->running = 1; return HAL_OK; }
HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *htim, uint32_t channel)
{
    (void)channel;
    htim->running = 1;
    return HAL_OK;
}
void hostsim_set_compare(TIM_HandleTypeDef *htim, uint32_t channel, uint32_t value)
{
    (void)channel;
    htim->ccr1 = value;
}

HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *huart, const uint8_t *data,
                                    uint16_t size, uint32_t timeout)
{
    (void)timeout;
    if (huart->Instance != USART3 || !uart3_out)
        return HAL_ERROR;
    for (uint16_t i = 0; i < size; i++)
    {
        fprintf(uart3_out, "%02x\n", data[i]);
        uart3_count++;
    }
    return HAL_OK;
}

int main(int argc, char **argv)
{
#ifdef _WIN32
    /* 텍스트 모드는 \r\n을 \n으로 바꾸므로 Serial Monitor가 보낸 바이트를 그대로 받도록 이진 모드로 연다. */
    _setmode(_fileno(stdin), _O_BINARY);
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    if (argc > 1)
    {
        uart3_out = fopen(argv[1], "w");
        if (!uart3_out)
        {
            perror(argv[1]);
            return 1;
        }
    }
    ece2_474_init();
    while (!feof(stdin))
        polling_routine();
    if (uart3_out)
    {
        fclose(uart3_out);
        fprintf(stderr, "UART3 bytes: %d -> %s\n", uart3_count, argv[1]);
    }
    return 0;
}
