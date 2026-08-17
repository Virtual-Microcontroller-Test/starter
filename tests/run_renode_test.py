import argparse
import os
import random
import socket
import subprocess
import sys
import tempfile
import time


IAC = 0xFF
CMD_WILL = 0xFB
CMD_WONT = 0xFC
CMD_DO = 0xFD
CMD_DONT = 0xFE
CMD_SB = 0xFA
CMD_SE = 0xF0


def strip_telnet(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(data):
        b = data[i]
        if b != IAC:
            out.append(b)
            i += 1
            continue
        if i + 1 >= len(data):
            break
        cmd = data[i + 1]
        if cmd == IAC:
            out.append(IAC)
            i += 2
        elif cmd in (CMD_WILL, CMD_WONT, CMD_DO, CMD_DONT):
            i += 3
        elif cmd == CMD_SB:
            end = data.find(bytes([IAC, CMD_SE]), i + 2)
            if end == -1:
                break
            i = end + 2
        else:
            i += 2
    return bytes(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", required=True)
    parser.add_argument("--expected", default="Hello world!")
    parser.add_argument("--renode-bin", default=os.environ.get("RENODE_BIN", "renode"))
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    port = args.port or random.randint(20000, 40000)

    with tempfile.TemporaryDirectory() as tmp:
        resc = os.path.join(tmp, "test.resc")
        elf = os.path.abspath(args.elf)
        with open(resc, "w") as f:
            f.write(
                'using sysbus\n'
                'mach create "test"\n'
                'machine LoadPlatformDescription @platforms/boards/renesas-ck_ra6m5.repl\n'
                f'emulation CreateServerSocketTerminal {port} "uart"\n'
                'connector Connect sysbus.sci0 uart\n'
                f'sysbus LoadELF @{elf}\n'
                'start\n'
            )

        proc = subprocess.Popen(
            [args.renode_bin, "--disable-xwt", "--console", "-e", f'include @{resc}'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        try:
            deadline = time.time() + args.timeout
            sock = None
            while time.time() < deadline:
                if proc.poll() is not None:
                    break
                try:
                    sock = socket.create_connection(("127.0.0.1", port), timeout=1)
                    break
                except OSError:
                    time.sleep(0.2)

            if sock is None:
                output, _ = proc.communicate(timeout=5)
                print(output.decode(errors="replace"))
                raise SystemExit("renode did not open the UART socket or exited early")

            buf = b""
            with sock:
                sock.settimeout(1)
                first = b""
                while time.time() < deadline:
                    try:
                        first = sock.recv(4096)
                    except socket.timeout:
                        continue
                    if first:
                        break
                if not first:
                    print("FAIL: no data from Renode")
                    return 1
                neg = bytearray()
                i = 0
                while i < len(first):
                    if first[i] != IAC:
                        i += 1
                        continue
                    if i + 1 >= len(first):
                        break
                    cmd = first[i + 1]
                    if cmd == CMD_WILL:
                        opt = first[i + 2] if i + 2 < len(first) else 0
                        neg.extend([IAC, CMD_DO, opt])
                        i += 3
                    elif cmd == CMD_DO:
                        opt = first[i + 2] if i + 2 < len(first) else 0
                        neg.extend([IAC, CMD_WILL, opt])
                        i += 3
                    else:
                        i += 2
                if neg:
                    sock.sendall(bytes(neg))
                buf = strip_telnet(first)
                while time.time() < deadline:
                    try:
                        data = sock.recv(4096)
                    except socket.timeout:
                        continue
                    if not data:
                        break
                    buf += strip_telnet(data)
                    if args.expected.encode() in buf:
                        print("PASS: expected output found")
                        return 0
            print(f"FAIL: expected {args.expected!r} not found in output {buf!r}")
            return 1
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    sys.exit(main())
