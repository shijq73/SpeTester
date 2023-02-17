################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../utilities/ringbuffer/ringbuffer.c 

C_DEPS += \
./utilities/ringbuffer/ringbuffer.d 

OBJS += \
./utilities/ringbuffer/ringbuffer.o 


# Each subdirectory must supply rules for building sources it contributes
utilities/ringbuffer/%.o: ../utilities/ringbuffer/%.c utilities/ringbuffer/subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: MCU C Compiler'
	arm-none-eabi-gcc -std=gnu99 -D__REDLIB__ -DCPU_MIMXRT1011DAE5A -DCPU_MIMXRT1011DAE5A_cm7 -DSDK_DEBUGCONSOLE=1 -DXIP_EXTERNAL_FLASH=1 -DXIP_BOOT_HEADER_ENABLE=1 -DMCUXPRESSO_SDK -DCR_INTEGER_PRINTF -DPRINTF_FLOAT_ENABLE=0 -D__MCUXPRESSO -D__USE_CMSIS -DDEBUG -I"D:\projects\SpeTester\source" -I"D:\projects\SpeTester\inc" -I"D:\projects\SpeTester\utilities" -I"D:\projects\SpeTester\utilities\ringbuffer" -I"D:\projects\SpeTester\drivers" -I"D:\projects\SpeTester\device" -I"D:\projects\SpeTester\component\uart" -I"D:\projects\SpeTester\component\lists" -I"D:\projects\SpeTester\xip" -I"D:\projects\SpeTester\CMSIS" -I"D:\projects\SpeTester\board" -O0 -fno-common -g3 -c -ffunction-sections -fdata-sections -ffreestanding -fno-builtin -fmerge-constants -fmacro-prefix-map="$(<D)/"= -mcpu=cortex-m7 -mfpu=fpv5-sp-d16 -mfloat-abi=hard -mthumb -D__REDLIB__ -fstack-usage -specs=redlib.specs -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


clean: clean-utilities-2f-ringbuffer

clean-utilities-2f-ringbuffer:
	-$(RM) ./utilities/ringbuffer/ringbuffer.d ./utilities/ringbuffer/ringbuffer.o

.PHONY: clean-utilities-2f-ringbuffer

