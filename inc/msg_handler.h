/*
 * msg_handler.h
 *
 *  Created on: Nov 26, 2022
 *      Author: JackShi
 */

#ifndef MSG_HANDLER_H_
#define MSG_HANDLER_H_

#include "msg_def.h"
#include "stddef.h"
#include "stdint.h"

void handle_msg(uint8_t msg_id, uint8_t* _rx_buf, uint8_t msg_len);

#endif /* MSG_HANDLER_H_ */
