#!/usr/bin/env python3
"""IMAP proxy for 163.com — injects ID command after LOGIN."""
import asyncio
import sys

TARGET = ('imap.163.com', 993)
ID_CMD = b'aercid ID ("name" "aerc" "version" "0.21.0")\r\n'


async def handle(creader, cwriter):
    try:
        sreader, swriter = await asyncio.open_connection(*TARGET, ssl=True)
    except Exception as e:
        print(f"proxy: {e}", file=sys.stderr)
        cwriter.close()
        return

    # Forward greeting
    cwriter.write(await sreader.readline())
    await cwriter.drain()

    id_injected = False
    server_buf = b''

    async def server_to_client():
        nonlocal id_injected, server_buf
        while True:
            try:
                data = await sreader.read(4096)
            except Exception:
                break
            if not data:
                break
            server_buf += data
            # Inject ID after LOGIN OK
            if not id_injected:
                lines = server_buf.split(b'\r\n')
                for i, line in enumerate(lines[:-1]):
                    if b'OK' in line and b'LOGIN' in line:
                        id_injected = True
                        swriter.write(ID_CMD)
                        await swriter.drain()
                        break
            cwriter.write(data)
            await cwriter.drain()
        cwriter.close()

    async def client_to_server():
        while True:
            try:
                data = await creader.read(4096)
            except Exception:
                break
            if not data:
                break
            swriter.write(data)
            await swriter.drain()
        swriter.close()

    await asyncio.gather(client_to_server(), server_to_client())


async def main():
    server = await asyncio.start_server(handle, '127.0.0.1', 11143)
    print(f"163 IMAP proxy on 127.0.0.1:11143", file=sys.stderr)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
