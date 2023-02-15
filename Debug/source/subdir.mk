################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../source/hello_world.c \
../source/msg_handler.c \
../source/semihost_hardfault.c \
../source/serial_data_handler.c 

C_DEPS += \
./source/hello_world.d \
./source/msg_handler.d \
./source/semihost_hardfault.d \
./source/serial_data_handler.d 

OBJS += \
./source/hello_world.o \
./source/msg_handler.o \
./source/semihost_hardfault.o \
./source/serial_data_handler.o 


# Each subdirectory must supply rules for building sources it contributes
source/%.o: ../source/%.c source/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -std=gnu99 -D__REDLIB__ -DCPU_MIMXRT1011DAE5A -DCPU_MIMXRT1011DAE5A_cm7 -DSDK_DEBUGCONSOLE=1 -DXIP_EXTERNAL_FLASH=1 -DXIP_BOOT_HEADER_ENABLE=1 -DPRINTF_FLOAT_ENABLE=0 -DSCANF_FLOAT_ENABLE=0 -DPRINTF_ADVANCED_ENABLE=0 -DSCANF_ADVANCED_ENABLE=0 -DMCUXPRESSO_SDK -DCR_INTEGER_PRINTF -D__MCUXPRESSO -D__USE_CMSIS -DDEBUG -I"/Users/jshi/Development/projects/SpeTester/source" -I"/Users/jshi/Development/projects/SpeTester/inc" -I"/Users/jshi/Development/projects/SpeTester/utilities" -I"/Users/jshi/Development/projects/SpeTester/utilities/ringbuffer" -I"/Users/jshi/Development/projects/SpeTester/drivers" -I"/Users/jshi/Development/projects/SpeTester/device" -I"/Users/jshi/Development/projects/SpeTester/component/uart" -I"/Users/jshi/Development/projects/SpeTester/component/lists" -I"/Users/jshi/Development/projects/SpeTester/xip" -I"/Users/jshi/Development/projects/SpeTester/CMSIS" -I"/Users/jshi/Development/projects/SpeTester/board" -O0 -fno-common -g3 -c -ffunction-sections -fdata-sections -ffreestanding -fno-builtin -fmerge-constants -fmacro-prefix-map="$(<D)/"= -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -D__REDLIB__ -fstack-usage -specs=redlib.specs -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


clean: clean-source

clean-source:
	-$(RM) ./source/hello_world.d ./source/hello_world.o ./source/msg_handler.d ./source/msg_handler.o ./source/semihost_hardfault.d ./source/semihost_hardfault.o ./source/serial_data_handler.d ./source/serial_data_handler.o

.PHONY: clean-source

