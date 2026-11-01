void polling_routine(void)
{
    static uint32_t last_ms = 0;
    uint32_t now_ms = HAL_GetTick();
    if (now_ms - last_ms < 1000U) return;
    last_ms = now_ms;

    uint8_t tx = 0x55;
    HAL_GPIO_WritePin(SPI_CS_ece2_GPIO_Port,
                      SPI_CS_ece2_Pin, GPIO_PIN_RESET);
    HAL_StatusTypeDef result =
        HAL_SPI_Transmit(&hspi1, &tx, 1U, 100U);
    HAL_GPIO_WritePin(SPI_CS_ece2_GPIO_Port,
                      SPI_CS_ece2_Pin, GPIO_PIN_SET);

    printf("TX=%02X, result=%d\r\n",
           (unsigned int)tx, (int)result);
}
