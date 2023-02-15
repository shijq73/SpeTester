#include "serial_handler.h"
#include "stdint.h"
#include "stdio.h"
#include "fsl_lpuart.h"
#include "msg_handler.h"
#include "board.h"
#include <string.h>

/* === MACROS ============================================================== */

/**
 * \name UART COMMUNICATION FRAMING
 * \{
 */
#define PROTOCOL_ID                     (0x0)
/** The start of transmission delimiter. */
#define SOT                             (1)
/** The end of transmission delimiter. */
#define EOT                             (4)
/**
 * A UART state that expects a \ref SOT to be received as the next character.
 */
#define UART_RX_STATE_SOT               (1)
/**
 * A UART state that expects the length to be received as the next character.
 */
#define UART_RX_STATE_LENGTH            (2)
/**
 * A UART state that expects the next data character to be received.
 */
#define UART_RX_STATE_DATA              (3)
/**
 * A UART state that expects a \ref EOT to be received as the next character.
 */
#define UART_RX_STATE_EOT               (4)


#define SERIAL_RX_BUF_SIZE              (128)
#define SERIAL_TX_BUF_SIZE              (128)
#define SERIAL_BUF_COUNT                (3)
#define RX_RING_BUFFER_SIZE 						(128)

#define DEMO_LPUART          LPUART1
#define DEMO_LPUART_CLK_FREQ BOARD_DebugConsoleSrcFreq()

/* === Globals ============================================================= */

/* === Prototypes ========================================================== */
static void LPUART_UserCallback(LPUART_Type *base, lpuart_handle_t *handle, status_t status, void *userData);
static void process_incoming_data(void);
static void handle_incoming_msg();
static uint8_t* encode_msg_header(uint8_t *msg_buf, uint8_t msg_id);

/* === LOCALS ============================================================== */
static uint8_t _data_len = 0;
static uint8_t _rx_state = UART_RX_STATE_SOT;
static uint8_t _rx_len;
static uint8_t _rxRingBuffer[RX_RING_BUFFER_SIZE] = {0}; /* RX ring buffer. */
static uint8_t _data[SERIAL_RX_BUF_SIZE];
static uint8_t _rx_buf[SERIAL_RX_BUF_SIZE];
static uint8_t _tx_buf[SERIAL_BUF_COUNT][SERIAL_RX_BUF_SIZE];
static uint8_t *_rx_ptr;
static uint8_t _rx_index;
static uint8_t _buf_count = 0;
static uint8_t _head = 0;
static uint8_t curr_tx_buffer_index=0;
static lpuart_handle_t _lpuartHandle;
static volatile bool _txing   = false;
static volatile bool _rxing   = false;
static lpuart_transfer_t receiveXfer;
static lpuart_transfer_t sendXfer;

/* === IMPLEMENTATION ====================================================== */

void serial_init()
{
  lpuart_config_t config;
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
  LPUART_TransferCreateHandle(DEMO_LPUART, &_lpuartHandle, LPUART_UserCallback, NULL);
  LPUART_TransferStartRingBuffer(DEMO_LPUART, &_lpuartHandle, _rxRingBuffer, RX_RING_BUFFER_SIZE);
}

/* LPUART user callback */
void LPUART_UserCallback(LPUART_Type *base, lpuart_handle_t *handle, status_t status, void *userData)
{
    if (kStatus_LPUART_TxIdle == status)
    {
        if(_txing)
        {
          _txing    = false;
          _head++;
          _head %= SERIAL_BUF_COUNT;
          _buf_count--;
          curr_tx_buffer_index = 0;
        }
    }

    if (kStatus_LPUART_RxIdle == status)
    {
        _rxing     = false;
    }
}

void serial_data_handler()
{
	_rx_index = 0;

	uint32_t receivedBytes;
	uint32_t data_size = LPUART_TransferGetRxRingBufferLength(DEMO_LPUART, &_lpuartHandle);

	if(data_size)
	{
		receiveXfer.data = _data;
		receiveXfer.dataSize = data_size;

		LPUART_TransferReceiveNonBlocking(DEMO_LPUART, &_lpuartHandle, &receiveXfer, &receivedBytes);

		_data_len = data_size;

		uint8_t count = 50;
		while(count-- && _data_len)
		{
			/* Process each single byte */
		  process_incoming_data();
		  _data_len--;
		  _rx_index++;
		}
	}

  /* Tx processing */
	if (_buf_count != 0 && !_txing )
	{
			sendXfer.data = _tx_buf[_head];
			sendXfer.dataSize = _tx_buf[_head][1] + 3;
			_txing = true;
			LPUART_TransferSendNonBlocking(DEMO_LPUART, &_lpuartHandle, &sendXfer);
	}
}

static void process_incoming_data(void)
{
  switch (_rx_state)
  {
    case UART_RX_STATE_SOT:
      _rx_ptr = _rx_buf;

      /* A valid SOT is received when the rx state is in Idle
       * state  */
      if (SOT == _data[_rx_index])
      {
          _rx_state = UART_RX_STATE_LENGTH;
      }

      break;

    case UART_RX_STATE_LENGTH:
      /* Length byte has been received */
      _rx_len = _data[_rx_index];

      /* Change the sio rx state to receive the payload, if the length
       * is a nonzero
       */
      if (_rx_len)
      {
          _rx_state = UART_RX_STATE_DATA;
          *_rx_ptr = _rx_len;
          _rx_ptr++;
      }
      else
      {
          /* NULL message */
          _rx_ptr = _rx_buf;
          _rx_state = UART_RX_STATE_SOT;
      }

      break;

    case UART_RX_STATE_DATA:
      /* Receive the data payload of 'length' no. of  bytes */
      *_rx_ptr = _data[_rx_index];
      _rx_ptr++;
      _rx_len--;
      if (!_rx_len)
      {
        _rx_state = UART_RX_STATE_EOT;
      }

      break;

    case UART_RX_STATE_EOT:

      /* Valid EOT is received after reception of 'length' no of bytes
      **/
      if (EOT == _data[_rx_index])
      {
          /* Message received successfully */
          handle_incoming_msg();
      }

      /* Make rx buffer ready for next reception before handling
       * received data. */
      _rx_ptr = _rx_buf;
      _rx_state = UART_RX_STATE_SOT;
      break;

    default:
      /* Handling of invalid sio rx state */
      _rx_ptr = _rx_buf;
      _rx_state = UART_RX_STATE_SOT;
      break;
    }
}

static void handle_incoming_msg()
{
  uint8_t error_code = 0;

  // _rx_buf[0] is message length
  /* Check for protocol id is Performance Analyzer */
  if (PROTOCOL_ID != _rx_buf[1])
  {
    return;
  }

  /* Check for the error conditions */
  uint8_t msg_id = _rx_buf[2];

  /* Process the commands */
  handle_msg(msg_id, _rx_buf, _rx_buf[0]);
}

uint8_t *get_next_tx_buffer(void)
{
    //DEBUG_PRINT("get_next_tx_buffer\r\n");
    if (_buf_count != SERIAL_BUF_COUNT) {
        uint8_t *buf;
        uint8_t tail;

        tail = (_head + _buf_count) % SERIAL_BUF_COUNT;
        buf = (uint8_t *)(&_tx_buf[tail]);
        _buf_count++;
        /* Add message start character */
        *buf++ = SOT;
        return buf;
    }

    return NULL;
}

static uint8_t* encode_msg_header(uint8_t *msg_buf, uint8_t msg_id)
{
  /* Check if buffer could not be allocated */
  if (NULL == msg_buf)
  {
      return NULL;
  }

  /* Copy Len, Protocol Id, Msg Id parameters */
  *msg_buf++ = 0; //
  *msg_buf++ = PROTOCOL_ID; /* protocol id */
  *msg_buf++ = msg_id;

  return msg_buf;
}

void usr_identify_board_confirm(uint8_t status,
        uint8_t band,
        const char *mcu_soc_name,
        const char *trx_name,
        const char *board_name)
{
    uint8_t *msg_buf = get_next_tx_buffer();
    /* Pointer to size element - the content is written later. */
    uint8_t *msg_size_ptr = msg_buf;

    msg_buf = encode_msg_header(msg_buf, IDENTIFY_BOARD_REQ | REQ_CONFIRM_MASK);

    /* Copy confirmation payload */
    *msg_buf++ = status;
    *msg_buf++ = band;
    if (mcu_soc_name != NULL)
    {
        *msg_buf++ = strlen(mcu_soc_name);
        memcpy(msg_buf, mcu_soc_name, strlen(mcu_soc_name));
        msg_buf += strlen(mcu_soc_name);
    }
    else
    {
        *msg_buf++ = 0x00; /* Length byte 0 as no string present */
    }

    if (trx_name != NULL)
    {
        *msg_buf++ = strlen(trx_name);
        memcpy(msg_buf, trx_name, strlen(trx_name));
        msg_buf += strlen(trx_name);
    }
    else
    {
        *msg_buf++ = 0x00; /* Length byte 0 as no string present */
    }

    if (board_name != NULL)
    {
        *msg_buf++ = strlen(board_name);
        memcpy(msg_buf, board_name, strlen(board_name));
        msg_buf += strlen(board_name);
    }
    else
    {
        *msg_buf++ = 0x00; /* Length byte 0 as no string present */
    }


    *msg_size_ptr = msg_buf-msg_size_ptr-1;

    *msg_buf = EOT;
}


void adc_req_confirm(uint8_t status, uint8_t start_stop)
{
    uint8_t *msg_buf = get_next_tx_buffer();
    /* Pointer to size element - the content is written later. */
    uint8_t *msg_size_ptr = msg_buf;

    msg_buf = encode_msg_header(msg_buf, ADC_REQ | REQ_CONFIRM_MASK);

    /* Copy confirmation payload */
    *msg_buf++ = status;
    *msg_buf++ = start_stop;

    *msg_size_ptr = msg_buf-msg_size_ptr-1;

    *msg_buf = EOT;
}

void dac_req_confirm(uint8_t status, uint8_t start_stop)
{
    uint8_t *msg_buf = get_next_tx_buffer();
    /* Pointer to size element - the content is written later. */
    uint8_t *msg_size_ptr = msg_buf;

    msg_buf = encode_msg_header(msg_buf, DAC_REQ | REQ_CONFIRM_MASK);

    /* Copy confirmation payload */
    *msg_buf++ = status;
    *msg_buf++ = start_stop;

    *msg_size_ptr = msg_buf-msg_size_ptr-1;

    *msg_buf = EOT;
}


void adc_ind(uint8_t status, uint16_t *result)
{
  uint8_t *msg_buf = get_next_tx_buffer();

  if(msg_buf == NULL) return;

  /* Pointer to size element - the content is written later. */
  uint8_t *msg_size_ptr = msg_buf;

  msg_buf = encode_msg_header(msg_buf, ADC_REQ | IND_MASK);

  /* Copy confirmation payload */
  *msg_buf++ = status;

  memcpy(msg_buf,result,20*sizeof(uint16_t));
  msg_buf += 20*sizeof(uint16_t);
  *msg_size_ptr = msg_buf-msg_size_ptr-1;

  *msg_buf = EOT;
}
