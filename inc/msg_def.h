/*
 * msg_def.h
 *
 *  Created on: Nov 26, 2022
 *      Author: JackShi
 */

#ifndef MSG_DEF_H_
#define MSG_DEF_H_

#define REMOTE_CMD_MASK                   (0x80)
#define REQ_CONFIRM_MASK                  (0x40)
#define IND_MASK                          (0x20)
#define MESSAGE_ID_MASK                   (0x1F)

enum msg_code {
    IDENTIFY_BOARD_REQ              =     (0x00),
    GPIO_READ_REQ                   =     (0x01),
    GPIO_WRITE_REQ                  =     (0x02),
    ADC_REQ                         =     (0x03),
    DAC_REQ                         =     (0x04),
    /* Confirms = Req | REQ_CONFIRM_MASK */
};

#endif /* MSG_DEF_H_ */
