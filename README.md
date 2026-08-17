# CK-RA6M5 Starter Project

Bare-metal C starter for the Renesas CK-RA6M5 board (R7FA6M5B, ARM Cortex-M33).

## Build

Requirements: `arm-none-eabi-gcc` (13.2) and GNU Make.

```bash
make
```

Produces `app.elf` and `app.hex`.

## Run in Renode

Requirements: Renode on your `PATH`.

```bash
make test
```

Loads `app.elf` onto the CK-RA6M5 platform and expects `Hello world!` on SCI0.

## Structure

- `link.ld` - memory layout (flash 0x0, SRAM 0x20000000)
- `startup.c` - vector table and reset handler
- `uart.c` - SCI0 UART driver (base 0x40118000)
- `main.c` - entry point

## CI

Every push to GitHub builds, verifies in Renode, and uploads `app.elf` as an
artifact. Add the `BACKEND_WEBHOOK_URL` and `BACKEND_WEBHOOK_SECRET` repository
secrets to notify the simulator backend.
