#ifndef __SERIAL_HANDLER_H_
#define __SERIAL_HANDLER_H_

#include "stdint.h"

void serial_init();
void serial_data_handler();
uint8_t *get_next_tx_buffer(void);

void usr_identify_board_confirm(uint8_t status,
        uint8_t band,
        const char *mcu_soc_name,
        const char *trx_name,
        const char *board_name);

void adc_req_confirm(uint8_t status, uint8_t start_stop);
void dac_req_confirm(uint8_t status, uint8_t start_stop);
void adc_ind(uint8_t status, uint16_t *result);

#endif //#ifndef __SERIAL_HANDLER_H_
