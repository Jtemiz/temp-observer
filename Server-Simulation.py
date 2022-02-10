import datetime
import random
import socket
import time


def runServer():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    i = 0
    while True:
        i += 1
        if i == 5:
            sock.sendto(bytes("STAT " + str(datetime.datetime.now()), "ascii"), ("127.0.0.1", 5100))
        sock.sendto(genMessage(i), ("127.0.0.1", 5100))
        time.sleep(5)


def genMessage(index):
    str = "VALUE;{index};{time};{temp1};{temp2};{temp3};{temp4}"
    return bytes(
        str.format(index=index, time=datetime.datetime.now(), temp1=random.random() * 90, temp2=random.random() * 90, temp3=random.random() * 90,
                   temp4=random.random() * 90), 'ascii')


runServer()
