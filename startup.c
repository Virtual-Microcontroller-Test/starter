#include <stdint.h>

extern int main(void);

void Default_Handler(void)
{
    for (;;) { }
}

void Reset_Handler(void);

__attribute__((used, section(".isr_vector"), aligned(8)))
void (*const g_pfnVectors[])(void) = {
    (void (*)(void))0x20080000,
    Reset_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
    Default_Handler,
};

extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;
extern uint32_t _data_load;

void Reset_Handler(void)
{
    uint32_t *src = &_data_load;
    uint32_t *dst = &_sdata;

    while (dst < &_edata) {
        *dst++ = *src++;
    }

    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }

    main();

    for (;;) { }
}
