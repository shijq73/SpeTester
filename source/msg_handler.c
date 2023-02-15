/*
 * msg_handler.c
 *
 *  Created on: Nov 26, 2022
 *      Author: JackShi
 */
#include "msg_handler.h"
#include "serial_handler.h"
#include "fsl_gpio.h"
//#include "adc.h"
//#include "dac.h"

typedef struct {
  uint8_t msg_id;
  void (*cmd_func)(uint8_t* rx_buf, uint8_t error_code);
} dsc_eval_cmd_t;

static void identify_board_req(uint8_t* rx_buf, uint8_t error_code);

#if 0
static void gpio_read_req(uint8_t* rx_buf, uint8_t error_code);
static void gpio_write_req(uint8_t* rx_buf, uint8_t error_code);
static void adc_req(uint8_t* rx_buf, uint8_t error_code);
static void dac_req(uint8_t* rx_buf, uint8_t error_code);
#endif

static void get_board_details(void);

dsc_eval_cmd_t const cmd_table[] = {
    {IDENTIFY_BOARD_REQ,      identify_board_req},
    //{GPIO_READ_REQ,           gpio_read_req},
    //{GPIO_WRITE_REQ,          gpio_write_req},
    //{ADC_REQ,                 adc_req},
    //{DAC_REQ,                 dac_req},
};

static size_t cmd_table_size = sizeof(cmd_table)/sizeof(dsc_eval_cmd_t);


void handle_msg(uint8_t msg_id, uint8_t* _rx_buf, uint8_t msg_len)
{
  for(uint32_t index=0; index<cmd_table_size; index++)
  {
    const dsc_eval_cmd_t *perf_cmd = &cmd_table[index];
    if(msg_id == perf_cmd->msg_id)
    {
      if(perf_cmd->cmd_func != NULL)
      {
        perf_cmd->cmd_func(_rx_buf, 0);
      }
    }
  }
}

static void identify_board_req(uint8_t* rx_buf, uint8_t error_code)
{
    (void)rx_buf;
    (void)error_code;
    /* For GUI development purpose removed the valid
     * state checking to execute this cmd
     */
    get_board_details();
    //node_info.mode=1;
}

static void get_board_details(void)
{
    uint8_t fw_ver[4];// = {FW_VER_0,FW_VER_1,FW_VER_2,FW_VER_3};

    /* Enable the mask bit for single/multi channel selection
    * feature is available in the firmware
    */
    //fw_feature_mask |= MULTI_CHANNEL_SELECT;
    //fw_feature_mask |= PER_RANGE_TEST_MODE;
    //fw_feature_mask |= PER_REMOTE_CONFIG_MODE;
    //fw_feature_mask |= PKT_STREAMING_MODE;
    //fw_feature_mask |= CONTINUOUS_RX_ON_MODE;
    //fw_feature_mask |= POWER_ON_CW_MODE;

    /* Send the Confirmation with the status as SUCCESS */
    usr_identify_board_confirm(0,
            1,
            (char const*)"NXP RT1010",
            (char const*)"EVAL",
            (char const*)"DSC EVAL");

}

#if 0
// -----------------------------------------------
// | msg_len | protocol_id | msg_id | port | pin |
// -----------------------------------------------
static void gpio_read_req(uint8_t* rx_buf, uint8_t error_code)
{
  uint8_t port = rx_buf[3];
  uint8_t pin = rx_buf[4];
}

// -------------------------------------------------------
// | msg_len | protocol_id | msg_id | port | pin | state |
// -------------------------------------------------------
static void gpio_write_req(uint8_t* rx_buf, uint8_t error_code)
{
  uint8_t port_index = rx_buf[3];
  uint8_t pin_index = rx_buf[4];
  uint8_t state = rx_buf[5];

  if(port_index<0 || port_index>5)
  {
    return;
  }

  GPIO_Type* port = (GPIO_Type*)((uint32_t)GPIOA+0x10*port_index);
  gpio_pin_t pin = kGPIO_Pin0<<pin_index;

  /* Define the init structure for the output LED pin*/
  gpio_config_t sOutputConfig = {
      .eDirection     = kGPIO_DigitalOutput,
      .eMode          = kGPIO_ModeGpio,
      .eOutMode       = kGPIO_OutputPushPull,
      .eSlewRate      = kGPIO_SlewRateFast,
      .eOutLevel      = kGPIO_OutputHigh,
      .eDriveStrength = kGPIO_DriveStrengthHigh,
      .ePull          = kGPIO_PullDisable,
      .eInterruptMode = kGPIO_InterruptDisable,
  };

  GPIO_PinInit(port, pin, &sOutputConfig);

  if(state)
  {
    GPIO_PinSet(port, pin);
  }
  else
  {
    GPIO_PinClear(port, pin);
  }
}

static void adc_req(uint8_t* rx_buf, uint8_t error_code)
{
    uint8_t msg_len =  rx_buf[0];
    uint8_t start_stop = rx_buf[3];
    if(start_stop)
    {
        uint8_t dma_en = rx_buf[4];
        uint8_t scan_mode = rx_buf[5];
        uint8_t* slots = &rx_buf[6];

        if(msg_len != 25)
        {
            adc_req_confirm(-1, start_stop);
        }
        adc_init(scan_mode, dma_en, slots);
        adc_req_confirm(0, start_stop);
    }
    else
    {
        adc_stop();
        adc_req_confirm(0, start_stop);
    }
}

static void dac_req(uint8_t* rx_buf, uint8_t error_code)
{
    uint8_t msg_len =  rx_buf[0];
    uint8_t action = rx_buf[3];

    switch(action)
    {
    case 0:
      dac_stop();
      dac_req_confirm(0, action);
      break;
    case 1:
      dac_start();
      dac_req_confirm(0, action);
      break;
    case 2:
      if(msg_len != 5)
      {
          dac_req_confirm(-1, action);
      }
      else
      {
          uint16_t dac_val = (uint16_t)(rx_buf[5] << 8) | rx_buf[4];
          dac_write(dac_val);
          dac_req_confirm(0, action);
      }
      break;
    default:
      dac_req_confirm(-1, action);
      break;
    }
}

#endif
