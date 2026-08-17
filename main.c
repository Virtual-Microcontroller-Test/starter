void uart_init(void);
void uart_puts(const char *s);

int main(void)
{
    uart_init();
    uart_puts("Hello world!\n");

    for (;;) { }
}
