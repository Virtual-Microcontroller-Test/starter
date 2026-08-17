CROSS  = arm-none-eabi-
CC     = $(CROSS)gcc
OBJCOPY = $(CROSS)objcopy
PYTHON ?= python3

CFLAGS  = -mcpu=cortex-m33 -mthumb -mfloat-abi=soft -nostdlib -ffreestanding -Os -Wall -Wextra -Werror -ffunction-sections -fdata-sections
LDFLAGS = -T link.ld -Wl,--gc-sections -Wl,-Map=app.map

SRCS = startup.c uart.c main.c
OBJS = $(SRCS:.c=.o)

all: app.elf app.hex

app.elf: $(OBJS) link.ld
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

app.hex: app.elf
	$(OBJCOPY) -O ihex $< $@

clean:
	rm -f $(OBJS) app.elf app.hex app.map

test: app.elf
	$(PYTHON) tests/run_renode_test.py --elf app.elf --expected "Hello world!"

.PHONY: all clean test
