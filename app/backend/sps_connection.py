import datetime
import logging
import socket
import traceback
# socket-adresses for communicating with Arduino
import socketserver
import threading

import app.globals
from app.globals import VALUES, LONGTERM_VALUES
from app.backend.db_connection import insertValue
ARD_UDP_IP_SEND = "192.168.5.2"
ARD_UDP_PORT_SEND = 9000
ARD_UDP_IP_RECEIVE = "127.0.0.1"
ARD_UDP_PORT_RECEIVE = 5100

# Arduino-Messages
ARD_Start = bytes("070", "ascii")
ARD_Stop = bytes("071", "ascii")
ARD_Kali = bytes("072", "ascii")
ARD_StartReset = bytes("073", "ascii")
ARD_SDRead = bytes("074", "ascii")

def sendStatus():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(app.globals.IS_LISTING, (ARD_UDP_IP_SEND, ARD_UDP_PORT_SEND))
        sock.close()
    except Exception as ex:
        logging.error("arduino_connection.sendStatus(): " + str(ex) +
                      "\n" + traceback.format_exc())

def startReset_Arduino():
    try:
        LONGTERM_VALUES.clear()
        VALUES.clear()
        SUDPServer.start_server()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(ARD_StartReset, (ARD_UDP_IP_SEND, ARD_UDP_PORT_SEND))
        sock.close()
    except Exception as ex:
        logging.error("arduino_connection.startReset_Arduino(): " + str(ex) +
                    "\n" + traceback.format_exc())

class MyUDPRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        message = self.rfile.readline().strip().decode('UTF-8')
        if "STAT" in message:
            self.readStatus(message)
        if "VALUE" in message:
            typeDataSplit = message.split(";")
            data = {
                "index": int(typeDataSplit[1]),
                "time": typeDataSplit[2],
                "temp1": float(typeDataSplit[3]),
                "temp2": float(typeDataSplit[4]),
                "temp3": float(typeDataSplit[5]),
                "temp4": float(typeDataSplit[6])
            }
            VALUES.append(data)
            insertValue(data)

    def readStatus(self, message):
        print(message)
        return

# This class provides a multithreaded UDP server that can receive messages sent to the defined ip and port
class UDPServer(threading.Thread):
    server_address = (ARD_UDP_IP_RECEIVE, ARD_UDP_PORT_RECEIVE)
    udp_server_object = None

    def run(self):
        try:
            self.udp_server_object = socketserver.ThreadingUDPServer(self.server_address, MyUDPRequestHandler)
            self.udp_server_object.serve_forever()
        except Exception as ex:
            logging.error("UDPServer.run(): " + str(ex) + "\n" + traceback.format_exc())

    def stop(self):
        try:
            self.udp_server_object.shutdown()
        except Exception as ex:
            logging.error("UDPServer.stop(): " + str(ex) + "\n" + traceback.format_exc())


class SUDPServer():
    __server: socketserver.ThreadingUDPServer = None

    @staticmethod
    def start_server():
        print("Server Started")
        if SUDPServer.__server == None:
            SUDPServer()
            SUDPServer.__server.start()
    @staticmethod
    def stop_server():
        if SUDPServer.__server != None:
            SUDPServer.__server.stop()
            SUDPServer.__server = None

    def __init__(self):
        if SUDPServer.__server is not None:
            raise Exception("Class is already initialized")
        SUDPServer.__server = UDPServer()

