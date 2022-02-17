import datetime
import random
import socket
import time

temps = [5, 5, 5, 5]
median = 70

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
    changeTemps()
    return bytes(
        str.format(index=index, time=datetime.datetime.now(), temp1=temps[0], temp2=temps[1], temp3=temps[2],
                   temp4=temps[3]), 'ascii')

def changeTemps():
    global temps
    for i in range(len(temps)):
        if temps[i] < median * 1.05:
            temps[i] += random.random()*5
        else:
            temps[i] -= random.random()*5
    print(temps)

runServer()
