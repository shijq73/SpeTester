/*
 * Copyright (c) 2013 - 2015, Freescale Semiconductor, Inc.
 * Copyright 2016-2017 NXP
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

#include "pin_mux.h"
#include "clock_config.h"
#include "board.h"
#include "fsl_lpuart.h"

/*******************************************************************************
 * Definitions
 ******************************************************************************/
#define DEMO_LPUART          LPUART1
#define DEMO_LPUART_CLK_FREQ BOARD_DebugConsoleSrcFreq()

#define RX_RING_BUFFER_SIZE 20U
#define ECHO_BUFFER_SIZE    8U
/*******************************************************************************
 * Prototypes
 ******************************************************************************/

/* LPUART user callback */
void LPUART_UserCallback(LPUART_Type *base, lpuart_handle_t *handle, status_t status, void *userData);

/*******************************************************************************
 * Variables
 ******************************************************************************/
lpuart_handle_t g_lpuartHandle;
uint8_t g_tipString[] = "LPUART RX ring buffer example\r\nSend back received data\r\nEcho every 8 types\r\n";
uint8_t g_rxRingBuffer[RX_RING_BUFFER_SIZE] = {0}; /* RX ring buffer. */

uint8_t g_rxBuffer[ECHO_BUFFER_SIZE] = {0}; /* Buffer for receive data to echo. */
uint8_t g_txBuffer[ECHO_BUFFER_SIZE] = {0}; /* Buffer for send data to echo. */
volatile bool rxBufferEmpty          = true;
volatile bool txBufferFull           = false;
volatile bool txOnGoing              = false;
volatile bool rxOnGoing              = false;

/*******************************************************************************
 * Code
 ******************************************************************************/

/* LPUART user callback */
void LPUART_UserCallback(LPUART_Type *base, lpuart_handle_t *handle, status_t status, void *userData)
{
    if (kStatus_LPUART_TxIdle == status)
    {
        txBufferFull = false;
        txOnGoing    = false;
    }

    if (kStatus_LPUART_RxIdle == status)
    {
        rxBufferEmpty = false;
        rxOnGoing     = false;
    }
}

/*!
 * @brief Main function
 */
int main(void)
{
    lpuart_config_t config;
    lpuart_transfer_t xfer;
    lpuart_transfer_t sendXfer;
    lpuart_transfer_t receiveXfer;
    size_t receivedBytes = 0U;
    uint32_t i;

    BOARD_ConfigMPU();
    BOARD_InitBootPins();
    BOARD_InitBootClocks();

    /*
     * config.baudRate_Bps = 115200U;
     * config.parityMode = kLPUART_ParityDisabled;
     * config.stopBitCount = kLPUART_OneStopBit;
     * config.txFifoWatermark = 0;
     * config.rxFifoWatermark = 0;
     * config.enableTx = false;
     * config.enableRx = false;
     */
    LPUART_GetDefaultConfig(&config);
    config.baudRate_Bps = BOARD_DEBUG_UART_BAUDRATE;
    config.enableTx     = true;
    config.enableRx     = true;

    LPUART_Init(DEMO_LPUART, &config, DEMO_LPUART_CLK_FREQ);
    LPUART_TransferCreateHandle(DEMO_LPUART, &g_lpuartHandle, LPUART_UserCallback, NULL);
    LPUART_TransferStartRingBuffer(DEMO_LPUART, &g_lpuartHandle, g_rxRingBuffer, RX_RING_BUFFER_SIZE);

    /* Send g_tipString out. */
    xfer.data     = g_tipString;
    xfer.dataSize = sizeof(g_tipString) - 1;
    txOnGoing     = true;
    LPUART_TransferSendNonBlocking(DEMO_LPUART, &g_lpuartHandle, &xfer);

    /* Wait send finished */
    while (txOnGoing)
    {
    }

    /* Start to echo. */

    receiveXfer.data     = g_rxBuffer;
    receiveXfer.dataSize = ECHO_BUFFER_SIZE;

    uint32_t data_size = 0;
    while (1)
    {
        /* If g_txBuffer is empty and g_rxBuffer is full, copy g_rxBuffer to g_txBuffer. */
        if (data_size)
        {
            memcpy(g_txBuffer, g_rxBuffer, data_size);
            rxBufferEmpty = true;
            txBufferFull  = true;
        }

        /* If TX is idle and g_txBuffer is full, start to send data. */
        if ((!txOnGoing) && data_size)
        {
            sendXfer.data        = g_txBuffer;
            sendXfer.dataSize    = data_size;
            txOnGoing = true;
            LPUART_TransferSendNonBlocking(DEMO_LPUART, &g_lpuartHandle, &sendXfer);
        }


        data_size = LPUART_TransferGetRxRingBufferLength(DEMO_LPUART, &g_lpuartHandle);
        if(data_size)
        {
          receiveXfer.data = g_rxBuffer;
          receiveXfer.dataSize = data_size;

          LPUART_TransferReceiveNonBlocking(DEMO_LPUART, &g_lpuartHandle, &receiveXfer, &receivedBytes);
          rxBufferEmpty = false;
          rxOnGoing     = false;
        }
#if 0
        /* If RX is idle and g_rxBuffer is empty, start to read data to g_rxBuffer. */
        if ((!rxOnGoing) && rxBufferEmpty)
        {
            rxOnGoing = true;
            LPUART_TransferReceiveNonBlocking(DEMO_LPUART, &g_lpuartHandle, &receiveXfer, &receivedBytes);
            if (ECHO_BUFFER_SIZE == receivedBytes)
            {
                rxBufferEmpty = false;
                rxOnGoing     = false;
            }
        }
#endif


        /* Delay some time, simulate the app is processing other things, input data save to ring buffer. */
        i = 0x10U;
        while (i--)
        {
            __NOP();
        }
    }
}
