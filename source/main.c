#include "board.h"
#include "clock_config.h"
#include "pin_mux.h"
#include "serial_handler.h"

/*******************************************************************************
 * Definitions
 ******************************************************************************/


/*******************************************************************************
 * Prototypes
 ******************************************************************************/

/*******************************************************************************
 * Code
 ******************************************************************************/
/*!
 * @brief Main function
 */
int main(void)
{
    /* Init board hardware. */
  BOARD_ConfigMPU();
  BOARD_InitBootPins();
  BOARD_InitBootClocks();

  serial_init();
  //init_sw_timer();

  uint32_t temp = 0;
  while (1)
  {
    //serial_data_handler();
    //sw_timer_tick();
  }
}
