/*
 * 표준 입출력 연결 코드입니다.
 * 이 파일은 CubeMX 자동 생성 파일이 아닙니다.
 * printf는 컴퓨터로 글자를 보내고, getchar·fgets·scanf는 컴퓨터에서 입력을 받습니다.
 * 통신에는 UART2와 보드의 ST-LINK USB 연결을 사용합니다. 속도는 9600입니다.
 */
#include "ece2_474.h"
#include "main.h"

/* UART2 설정은 CubeMX가 main.c에 생성합니다. 여기서는 그 설정을 사용합니다. */

/* printf가 출력할 문자 한 개를 컴퓨터로 보냅니다.
 * 전송에 실패하면 EOF를 반환합니다.
 */
int __io_putchar(int ch)
{
    /* 전달받은 문자를 한 바이트로 바꾸어 전송합니다. */
    uint8_t byte = (uint8_t)ch;
    if (HAL_UART_Transmit(&huart2, &byte, 1, 100) != HAL_OK)
    {
        return EOF;
    }
    return (unsigned char)ch;
}
/* 컴퓨터에서 문자 한 개가 도착할 때까지 기다린 뒤 반환합니다.
 * 입력을 기다리는 동안 이 함수를 호출한 코드의 다음 줄은 실행되지 않습니다.
 * 메인 코드에서 사용하며, 인터럽트 처리 함수 안에서는 호출하지 않습니다.
 */
int __io_getchar(void)
{
    uint8_t byte;
    if (HAL_UART_Receive(&huart2, &byte, 1, HAL_MAX_DELAY) != HAL_OK)
    {
        return EOF;
    }
    return byte;
}
/* 표준 입력 함수가 사용하는 연결 함수입니다.
 * CubeMX가 syscalls.c에 만든 기본 _read 대신 이 함수를 사용합니다.
 * 요청한 길이가 길어도 문자 한 개를 받으면 바로 반환하여 불필요한 대기를 줄입니다.
 */
int _read(int file, char *ptr, int len)
{
    /* 표준 입력을 모두 UART2로 받으므로 파일 번호는 사용하지 않습니다. */
    (void)file;
    if (len <= 0)
    {
        return 0;
    }

    int ch = __io_getchar();
    if (ch == EOF)
    {
        return -1;
    }
    /* 받은 문자를 저장하고, 읽은 문자 수 1을 반환합니다. */
    ptr[0] = (char)ch;
    return 1;
}
