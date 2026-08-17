#include <stdint.h>

#define SCI0_BASE 0x40118000UL

#define SCI_SMR (*(volatile uint8_t *)(SCI0_BASE + 0x00))
#define SCI_BRR (*(volatile uint8_t *)(SCI0_BASE + 0x01))
#define SCI_SCR (*(volatile uint8_t *)(SCI0_BASE + 0x02))
#define SCI_TDR (*(volatile uint8_t *)(SCI0_BASE + 0x03))
#define SCI_SSR (*(volatile uint8_t *)(SCI0_BASE + 0x04))

#define SCR_RE   (1u << 4)
#define SCR_TE   (1u << 5)
#define SSR_TDRE (1u << 7)

void uart_init(void)
{
    SCI_SCR = 0;
    SCI_SMR = 0;
    SCI_BRR = 216;
    SCI_SCR = SCR_RE | SCR_TE;
}

void uart_putc(char c)
{
    while (!(SCI_SSR & SSR_TDRE)) { }
    SCI_TDR = (uint8_t)c;
}

void uart_puts(const char *s)
{
    while (*s) {
        uart_putc(*s++);
    }
}
