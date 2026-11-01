/* STM32_3 호스트 시뮬레이션.
 * 보드에 올릴 ece2_474_routine.c를 PC에서 그대로 컴파일하고 ece2_474_init(), polling_routine()을 호출한다.
 *
 * 마스터(STM32_3_ROLE=1):  hostsim.exe master <초> <송신 바이트.hex> <파형.csv>
 *   - polling_routine()을 1 ms 간격(가상 시각)으로 부른다. HAL_GetTick()은 이 가상 시각이다.
 *   - HAL_SPI_Transmit이 받은 바이트를 한 줄에 하나씩 16진수로 적는다 → FPGA 수신 TB(lab7_01)가 읽는다.
 *   - 같은 바이트를 Mode 0 규칙(SCK 대기 LOW, 첫 비트를 첫 상승 에지 전에 준비, 하강 에지에서 다음 비트)으로
 *     SCK·MOSI·CS 시각표(CSV)로 펼치고, 상승 에지에서 MOSI를 읽어 다시 조립해 비트 순서를 확인한다.
 *     SCK 주기는 main.c 설정(100 MHz / 128 = 781.25 kHz, 1280 ns)이다.
 * 슬레이브(STM32_3_ROLE=2): hostsim.exe slave <수신 바이트.hex>
 *   - 파일의 한 줄 = 송신 측이 보낸 한 바이트(FPGA 송신 TB(lab7_02)가 MOSI에서 읽은 값).
 *     "--" 줄은 2초 동안 아무것도 오지 않은 경우(송신 측 꺼짐)로 HAL_TIMEOUT을 돌려준다.
 *   - HAL_SPI_Receive는 init에서 SPI1이 슬레이브·NSS 하드웨어 입력으로 바뀌었고 PA4가 AF5로 설정됐을 때만 받는다.
 * MCU → PC(VCP) printf 출력은 표준 출력으로 나온다. 실제 보드 측정이 아니라 실습 코드의 판단·출력 형식을 보는 논리 검증이다.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#include "ece2_474.h"
#include "main.h"

#define SCK_PERIOD_NS 1280U /* 781.25 kHz */

GPIO_TypeDef hostsim_gpioa = {0, 0, 'A'}, hostsim_gpiob = {0, 0, 'B'}, hostsim_gpioc = {0, 0, 'C'};
TIM_TypeDef hostsim_tim6, hostsim_tim3;
USART_TypeDef hostsim_usart2, hostsim_usart3;
SPI_TypeDef hostsim_spi1;
TIM_HandleTypeDef htim6 = {TIM6, 0, 0}, htim3 = {TIM3, 0, 500U};
UART_HandleTypeDef huart2 = {USART2}, huart3 = {USART3};
/* main.c의 MX_SPI1_Init 결과: 마스터, 소프트웨어 NSS, 분주비 128 */
SPI_HandleTypeDef hspi1 = {SPI1, {SPI_MODE_MASTER, SPI_NSS_SOFT, SPI_BAUDRATEPRESCALER_128}, 1};
I2C_HandleTypeDef hi2c1;

static uint32_t tick_ms;
static FILE *spi_out, *wave_out, *spi_in;
static int tx_count, decode_errors, pa4_af5;

void Error_Handler(void)
{
    fprintf(stderr, "Error_Handler called\n");
    exit(2);
}
uint32_t HAL_GetTick(void) { return tick_ms; }
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *port, uint16_t pin)
{
    return (port->idr & pin) ? GPIO_PIN_SET : GPIO_PIN_RESET;
}
void HAL_GPIO_WritePin(GPIO_TypeDef *port, uint16_t pin, GPIO_PinState state)
{
    port->odr = state == GPIO_PIN_SET ? (port->odr | pin) : (port->odr & (uint16_t)~pin);
}
void HAL_GPIO_TogglePin(GPIO_TypeDef *port, uint16_t pin) { port->odr ^= pin; }
void HAL_GPIO_Init(GPIO_TypeDef *port, GPIO_InitTypeDef *init)
{
    if (port == GPIOA && init->Pin == GPIO_PIN_4 && init->Mode == GPIO_MODE_AF_PP &&
        init->Alternate == GPIO_AF5_SPI1)
        pa4_af5 = 1;
}
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
    (void)huart; (void)data; (void)size; (void)timeout;
    return HAL_OK;
}

HAL_StatusTypeDef HAL_SPI_DeInit(SPI_HandleTypeDef *hspi)
{
    hspi->initialized = 0;
    return HAL_OK;
}
HAL_StatusTypeDef HAL_SPI_Init(SPI_HandleTypeDef *hspi)
{
    hspi->initialized = 1;
    return HAL_OK;
}

/* 한 바이트를 Mode 0 시각표로 펼쳐 CSV에 적고, 상승 에지에서 MOSI를 읽어 되돌린 값을 돌려준다. */
static uint8_t emit_mode0(uint8_t value, uint64_t t0)
{
    uint8_t got = 0;
    uint64_t t = t0;
    fprintf(wave_out, "%llu,0,0,%d\n", (unsigned long long)t, (value >> 7) & 1); /* CS LOW, 첫 비트 준비 */
    for (int i = 7; i >= 0; i--)
    {
        int bit = (value >> i) & 1;
        uint64_t rise = t + SCK_PERIOD_NS / 2U, fall = t + SCK_PERIOD_NS;
        fprintf(wave_out, "%llu,0,1,%d\n", (unsigned long long)rise, bit);
        got = (uint8_t)((got << 1) | bit);                    /* 수신 측: 상승 에지에서 읽음 */
        int next = i > 0 ? (value >> (i - 1)) & 1 : bit;      /* 하강 에지에서 다음 비트 준비 */
        fprintf(wave_out, "%llu,0,0,%d\n", (unsigned long long)fall, next);
        t = fall;
    }
    fprintf(wave_out, "%llu,1,0,%d\n", (unsigned long long)(t + SCK_PERIOD_NS / 2U), value & 1); /* CS HIGH */
    return got;
}

HAL_StatusTypeDef HAL_SPI_Transmit(SPI_HandleTypeDef *hspi, const uint8_t *data,
                                   uint16_t size, uint32_t timeout)
{
    (void)timeout;
    if (!hspi->initialized || hspi->Init.Mode != SPI_MODE_MASTER)
        return HAL_ERROR;
    if (SPI_CS_ece2_GPIO_Port->odr & SPI_CS_ece2_Pin)
        fprintf(stderr, "warning: t=%u ms CS(PB6) HIGH during transmit\n", tick_ms);
    for (uint16_t i = 0; i < size; i++)
    {
        fprintf(spi_out, "%02x\n", data[i]);
        uint8_t back = emit_mode0(data[i], (uint64_t)tick_ms * 1000000ULL);
        fprintf(stderr, "t=%5u ms  SPI TX %02X  MOSI bits(MSB first) ", tick_ms, data[i]);
        for (int b = 7; b >= 0; b--) fputc('0' + ((data[i] >> b) & 1), stderr);
        fprintf(stderr, "  rising-edge decode %02X %s\n", back, back == data[i] ? "OK" : "MISMATCH");
        if (back != data[i]) decode_errors++;
        tx_count++;
    }
    return HAL_OK;
}

HAL_StatusTypeDef HAL_SPI_Receive(SPI_HandleTypeDef *hspi, uint8_t *data,
                                  uint16_t size, uint32_t timeout)
{
    (void)timeout;
    if (!hspi->initialized || hspi->Init.Mode != SPI_MODE_SLAVE ||
        hspi->Init.NSS != SPI_NSS_HARD_INPUT || !pa4_af5)
        return HAL_ERROR;
    for (uint16_t i = 0; i < size; i++)
    {
        char line[32];
        if (!fgets(line, sizeof line, spi_in))
        {
            fflush(stdout);
            fprintf(stderr, "end of SPI input, received %d bytes\n", tx_count);
            exit(0);
        }
        if (line[0] == '-')
            return HAL_TIMEOUT;
        data[i] = (uint8_t)strtoul(line, NULL, 16);
        tx_count++;
    }
    return HAL_OK;
}

int main(int argc, char **argv)
{
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY); /* \r\n을 그대로 남긴다 */
#endif
    if (argc >= 5 && strcmp(argv[1], "master") == 0)
    {
        uint32_t end_ms = (uint32_t)atoi(argv[2]) * 1000U;
        spi_out = fopen(argv[3], "w");
        wave_out = fopen(argv[4], "w");
        if (!spi_out || !wave_out) { perror("output"); return 1; }
        fprintf(wave_out, "t_ns,cs,sck,mosi\n");
        HAL_GPIO_WritePin(SPI_CS_ece2_GPIO_Port, SPI_CS_ece2_Pin, GPIO_PIN_SET); /* main.c: CS 초기 HIGH */
        ece2_474_init();
        for (tick_ms = 0; tick_ms <= end_ms; tick_ms++)
            polling_routine();
        fclose(spi_out);
        fclose(wave_out);
        fprintf(stderr, "SPI TX bytes: %d, decode errors: %d\n", tx_count, decode_errors);
        return decode_errors ? 1 : 0;
    }
    if (argc >= 3 && strcmp(argv[1], "slave") == 0)
    {
        spi_in = fopen(argv[2], "r");
        if (!spi_in) { perror(argv[2]); return 1; }
        ece2_474_init();
        for (;;)
            polling_routine();
    }
    fprintf(stderr, "usage: %s master <sec> <out.hex> <wave.csv> | slave <in.hex>\n", argv[0]);
    return 1;
}
