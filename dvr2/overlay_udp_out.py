import socket
import random
import datetime
import time

conn = ("127.0.0.1", 20001)


def rand_value(f_val, t_val):
    result = round(random.uniform(f_val, t_val), 2)
    result = random.uniform(f_val, t_val)
    return result


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:

    time.sleep(1)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    overlay = timestamp

    for i in range(9):
        val = round(rand_value(i * 10, i * 10 + 10), 3)
        if i == 8:
            val = "TASK: I'm the real Batman"
        overlay = overlay + "," + str(val)

    print(overlay)
    sock.sendto(overlay.encode(), conn)
