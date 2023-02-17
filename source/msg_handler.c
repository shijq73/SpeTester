/*
 * msg_handler.c
 *
 *  Created on: Nov 26, 2022
 *      Author: JackShi
 */
#include "msg_handler.h"
#include "serial_handler.h"
#include "fsl_gpio.h"
#include "fsl_iomuxc.h"
//#include "adc.h"
//#include "dac.h"

#define user_gpio2_0_15_handler GPIO2_Combined_0_15_IRQHandler
#define user_gpio1_0_15_handler GPIO1_Combined_0_15_IRQHandler
#define user_gpio1_16_31_handler GPIO1_Combined_16_31_IRQHandler

typedef struct {
  uint8_t msg_id;
  void (*cmd_func)(uint8_t* rx_buf, uint8_t error_code);
} dsc_eval_cmd_t;

static void identify_board_req(uint8_t* rx_buf, uint8_t error_code);

static void gpio_irq_handler(void);

static void gpio_read_req(uint8_t* rx_buf, uint8_t error_code);
static void gpio_write_req(uint8_t* rx_buf, uint8_t error_code);
#if 0
static void adc_req(uint8_t* rx_buf, uint8_t error_code);
static void dac_req(uint8_t* rx_buf, uint8_t error_code);
#endif

static void get_board_details(void);

dsc_eval_cmd_t const cmd_table[] = {
    {IDENTIFY_BOARD_REQ,      identify_board_req},
    {GPIO_READ_REQ,           gpio_read_req},
    {GPIO_WRITE_REQ,          gpio_write_req},
    //{ADC_REQ,                 adc_req},
    //{DAC_REQ,                 dac_req},
};

static size_t cmd_table_size = sizeof(cmd_table)/sizeof(dsc_eval_cmd_t);


void user_gpio1_0_15_handler(void)
{
	uint32_t interrupt_flags = GPIO_GetPinsInterruptFlags(GPIO1);

	for (uint8_t pin=0; pin<16; pin++)
	{
		if ((GPIO1->IMR & (1U << pin)) &&  interrupt_flags & (1U<<pin))
		{
			uint32_t state = GPIO_PinRead(GPIO1, pin);

			gpio_read_ind(0, 0, pin, state);
		    /* clear the interrupt status */
		    GPIO_PortClearInterruptFlags(GPIO1, 1U << pin);
		}
	}

    /* Change state of switch. */
    SDK_ISR_EXIT_BARRIER;
}

void user_gpio1_16_31_handler(void)
{
	uint32_t interrupt_flags = GPIO_GetPinsInterruptFlags(GPIO1);

	for (uint8_t pin=16; pin<32; pin++)
	{
		if ((GPIO1->IMR & (1U << pin)) &&  interrupt_flags & (1U<<pin))
		{
			uint32_t state = GPIO_PinRead(GPIO1, pin);

			gpio_read_ind(0, 0, pin, state);
		    /* clear the interrupt status */
		    GPIO_PortClearInterruptFlags(GPIO1, 1U << pin);
		}
	}

    /* Change state of switch. */
    SDK_ISR_EXIT_BARRIER;
}

void user_gpio2_0_15_handler(void)
{
	uint32_t interrupt_flags = GPIO_GetPinsInterruptFlags(GPIO2);

	for (uint8_t pin=0; pin<16; pin++)
	{
		if ((GPIO2->IMR & (1U << pin)) &&  interrupt_flags & (1U<<pin))
		{
			uint32_t state = GPIO_PinRead(GPIO2, pin);

			gpio_read_ind(0, 1, pin, state);
		    /* clear the interrupt status */
		    GPIO_PortClearInterruptFlags(GPIO2, 1U << pin);
		}
	}

    /* Change state of switch. */
    SDK_ISR_EXIT_BARRIER;
}

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



// -----------------------------------------------
// | msg_len | protocol_id | msg_id | port | pin |
// -----------------------------------------------
static void gpio_read_req(uint8_t* rx_buf, uint8_t error_code)
{
  uint8_t peripheral_index = rx_buf[3];
  uint8_t pin_index = rx_buf[4];
  uint8_t start_stop = rx_buf[5];

  GPIO_Type *port;

  if(peripheral_index != 0 && peripheral_index != 1)
  {
    return;
  }

  if(peripheral_index == 0)
  {
    port = GPIO1;
  }

  if(peripheral_index == 1)
  {
    port = GPIO2;
  }

  uint32_t muxRegister;
  uint32_t inputRegister = 0;
  uint32_t configRegister;
  uint32_t inputDaisy = 0;
  uint32_t inputOnfield = 0;
  uint32_t muxMode = 5;
  uint32_t pin = pin_index;

  if( pin_index >= 29)
  {
	pin = pin_index-29;
  }

  if(start_stop != 0)
  {

	  if(pin_index < 14)
	  {
		muxRegister = 0x401F8088U + (13-pin_index)*4;
		configRegister = 0x401F8138U + (13-pin_index)*4;
	  }

	  if( pin_index >= 14 &&
		  pin_index < 29)
	  {
		muxRegister = 0x401F8010U + (28-pin_index)*4;
		configRegister = 0x401F80C0U + (28-pin_index)*4;
	  }

	  if( pin_index >= 29)
	  {
		muxRegister = 0x401F8050U + (42-pin_index)*4;
		configRegister = 0x401F8100U + (42-pin_index)*4;
		pin = pin_index-29;
	  }

	  IOMUXC_SetPinMux(muxRegister, muxMode, inputDaisy, inputRegister, configRegister, inputOnfield);

	#if 1
	  if(peripheral_index == 1 && pin_index<29)
	  {
		IOMUXC_GPR->GPR26 |= (1u << pin);
	  }
	  else
	  {
		IOMUXC_GPR->GPR26 &= ~(1u << pin);
	  }
	#endif
	  IOMUXC_SetPinConfig(muxRegister, muxMode, inputDaisy, inputRegister, configRegister, 0x01B0A0U);

	  gpio_pin_config_t input_config = {kGPIO_DigitalInput, 0, kGPIO_IntRisingOrFallingEdge};

	  //if(port == GPIO1)
	  if( pin_index < 29)
	  {
		  //EnableIRQ(GPIO1_Combined_0_15_IRQn);
		  EnableIRQ(GPIO1_Combined_16_31_IRQn);
		  GPIO_PinInit(GPIO1, pin, &input_config);
		  GPIO_PortEnableInterrupts(GPIO1, 1U << pin);
	  }
	  else
	  //if(port == GPIO2)
	  {
		  EnableIRQ(GPIO2_Combined_0_15_IRQn);
		  GPIO_PinInit(GPIO2, pin, &input_config);
		  GPIO_PortEnableInterrupts(GPIO2, 1U << pin);
	  }

	  //GPIO_PinInit(port, pin, &input_config);

	  //GPIO_PortEnableInterrupts(port, 1U << pin);
  }
  else
  {
	  GPIO_PortDisableInterrupts(port, 1U << pin);
  }

  gpio_read_confirm(0, start_stop);

}

// -------------------------------------------------------
// | msg_len | protocol_id | msg_id | port | pin | state |
// -------------------------------------------------------
static void gpio_write_req(uint8_t* rx_buf, uint8_t error_code)
{
  uint8_t peripheral_index = rx_buf[3];
  uint8_t pin_index = rx_buf[4];
  uint8_t state = rx_buf[5];
  GPIO_Type *port;

  if(peripheral_index != 0 && peripheral_index != 1)
  {
    return;
  }

  if(peripheral_index == 0)
  {
    port = GPIO1;
  }

  if(peripheral_index == 1)
  {
    port = GPIO2;
  }

  uint32_t muxRegister;
  uint32_t inputRegister = 0;
  uint32_t configRegister;
  uint32_t inputDaisy = 0;
  uint32_t inputOnfield = 0;
  uint32_t muxMode = 5;
  uint32_t pin = pin_index;

  if(pin_index < 14)
  {
    muxRegister = 0x401F8088U + (13-pin_index)*4;
    configRegister = 0x401F8138U + (13-pin_index)*4;
  }

  if( pin_index >= 14 &&
      pin_index < 29)
  {
    muxRegister = 0x401F8010U + (14-pin_index)*4;
    configRegister = 0x401F80C0U + (13-pin_index)*4;
  }

  if( pin_index >= 29)
  {
    muxRegister = 0x401F8050U + (28-pin_index)*4;
    configRegister = 0x401F8100U + (13-pin_index)*4;
    pin = pin_index-29;
  }

  IOMUXC_SetPinMux(muxRegister, muxMode, inputDaisy, inputRegister, configRegister, inputOnfield);

  if(peripheral_index == 1 && pin_index<29)
  {
    IOMUXC_GPR->GPR26 |= (1u << 11);
  }
  else
  {
    IOMUXC_GPR->GPR26 &= ~(1u << 11);
  }

  IOMUXC_SetPinConfig(muxRegister, muxMode, inputDaisy, inputRegister, configRegister, 0x01B0A0U);

  gpio_pin_config_t output_config = {kGPIO_DigitalOutput, 0, kGPIO_NoIntmode};

  GPIO_PinInit(port, pin, &output_config);

  if(state)
  {
    GPIO_PinWrite(port, pin, 1U);
  }
  else
  {
    GPIO_PinWrite(port, pin, 0U);
  }
}

#if 0
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
