import time

from gps_reader import GPS_UART_CONFIG, _parse_nmea_line

machine = __import__('machine')
UART = machine.UART


BAUD_RATES = [4800, 9600, 38400, 57600, 115200]
READ_WINDOW_MS = 5000
MAX_CHUNK_PREVIEW = 64


def _ticks_ms():
    ticks_ms = getattr(time, 'ticks_ms', None)
    if ticks_ms:
        return ticks_ms()
    return int(time.time() * 1000)


def _ticks_diff(current_ms, start_ms):
    ticks_diff = getattr(time, 'ticks_diff', None)
    if ticks_diff:
        return ticks_diff(current_ms, start_ms)
    return current_ms - start_ms


def _hex_preview(data):
    return ' '.join('%02X' % byte for byte in data[:MAX_CHUNK_PREVIEW])


def _ascii_preview(data):
    chars = []
    for byte in data[:MAX_CHUNK_PREVIEW]:
        if 32 <= byte <= 126:
            chars.append(chr(byte))
        elif byte in (10, 13):
            chars.append('\\n' if byte == 10 else '\\r')
        else:
            chars.append('.')
    return ''.join(chars)


def _extract_text_bytes(data):
    chars = []
    for byte in data:
        if 32 <= byte <= 126:
            chars.append(chr(byte))
        elif byte in (10, 13):
            chars.append(chr(byte))
    return ''.join(chars)


def _mask_7bit(data):
    return bytes(byte & 0x7F for byte in data)


def _run_one_baud(baudrate):
    print('\n=== BAUD %d ===' % baudrate)
    uart = UART(1,
                baudrate=baudrate,
                tx=GPS_UART_CONFIG['tx'],
                rx=GPS_UART_CONFIG['rx'],
                timeout=GPS_UART_CONFIG['timeout'])

    start_ms = _ticks_ms()
    buffer = ''
    masked_buffer = ''
    byte_count = 0
    line_count = 0
    parsed_count = 0
    masked_line_count = 0
    masked_parsed_count = 0
    saw_ubx = False
    chunk_count = 0

    try:
        while _ticks_diff(_ticks_ms(), start_ms) < READ_WINDOW_MS:
            if uart.any():
                raw = uart.read()
                if not raw:
                    time.sleep(0.05)
                    continue

                chunk_count += 1
                byte_count += len(raw)

                if b'\xB5\x62' in raw:
                    saw_ubx = True

                masked_raw = _mask_7bit(raw)

                print('[RAW HEX]', _hex_preview(raw))
                print('[RAW ASCII]', _ascii_preview(raw))
                print('[MASK7 HEX]', _hex_preview(masked_raw))
                print('[MASK7 ASCII]', _ascii_preview(masked_raw))

                chunk = _extract_text_bytes(raw)
                masked_chunk = _extract_text_bytes(masked_raw)
                buffer += chunk
                masked_buffer += masked_chunk

                if len(buffer) > 4096:
                    buffer = buffer[-2048:]
                if len(masked_buffer) > 4096:
                    masked_buffer = masked_buffer[-2048:]

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue

                    line_count += 1
                    print('[LINE]', line)
                    parsed = _parse_nmea_line(line)
                    if parsed:
                        lon, lat, alt = parsed
                        parsed_count += 1
                        print('[PARSED] lon=%s lat=%s alt=%s' % (lon, lat, alt))

                while '\n' in masked_buffer:
                    line, masked_buffer = masked_buffer.split('\n', 1)
                    line = line.strip()
                    if not line:
                        continue

                    masked_line_count += 1
                    print('[MASK7 LINE]', line)
                    parsed = _parse_nmea_line(line)
                    if parsed:
                        lon, lat, alt = parsed
                        masked_parsed_count += 1
                        print('[MASK7 PARSED] lon=%s lat=%s alt=%s' % (lon, lat, alt))

            time.sleep(0.05)

    finally:
        try:
            uart.deinit()
        except Exception:
            pass

    print('[SUMMARY] baud=%s bytes=%s chunks=%s lines=%s parsed=%s mask7_lines=%s mask7_parsed=%s ubx=%s'
          % (baudrate, byte_count, chunk_count, line_count, parsed_count, masked_line_count, masked_parsed_count, saw_ubx))

    return {
        'baudrate': baudrate,
        'byte_count': byte_count,
        'chunk_count': chunk_count,
        'line_count': line_count,
        'parsed_count': parsed_count,
        'masked_line_count': masked_line_count,
        'masked_parsed_count': masked_parsed_count,
        'saw_ubx': saw_ubx,
    }


def main():
    print('=== GPS standalone test start ===')
    print('UART1 tx={tx} rx={rx} baud_list={baud_list}'.format(
        tx=GPS_UART_CONFIG['tx'],
        rx=GPS_UART_CONFIG['rx'],
        baud_list=BAUD_RATES,
    ))
    print('Reading each baud for %d ms...' % READ_WINDOW_MS)

    results = []
    for baudrate in BAUD_RATES:
        results.append(_run_one_baud(baudrate))

    print('=== GPS standalone test end ===')
    for item in results:
        print('baud={baudrate} bytes={byte_count} lines={line_count} parsed={parsed_count} mask7_lines={masked_line_count} mask7_parsed={masked_parsed_count} ubx={saw_ubx}'.format(**item))

    parsed_results = [item for item in results if item['parsed_count'] > 0]
    masked_parsed_results = [item for item in results if item['masked_parsed_count'] > 0]
    ubx_results = [item for item in results if item['saw_ubx']]
    byte_results = [item for item in results if item['byte_count'] > 0]

    if parsed_results:
        best = parsed_results[0]
        print('结论：在 baud=%s 下已解析出有效 GPS 数据。' % best['baudrate'])
    elif masked_parsed_results:
        best = masked_parsed_results[0]
        print('结论：原始字节流高位疑似被污染，但在 baud=%s 下经 7-bit 掩码后可解析出 GPS 数据。' % best['baudrate'])
    elif ubx_results:
        print('结论：串口有数据且疑似 UBX 二进制协议，不是当前 NMEA 文本解析路径。')
    elif byte_results:
        print('结论：串口有字节流，但未形成可解析 NMEA。优先看哪个波特率的 RAW HEX/ASCII 最像文本。')
    else:
        print('结论：所有测试波特率都没有读到有效字节，优先检查接线、供电、模块输出状态。')


main()
