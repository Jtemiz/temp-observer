import logging
import socket
import traceback
import socketserver
import threading
from configparser import ConfigParser
from datetime import datetime

import app.globals as glob
from app.globals import VALUES
from app.backend.db_connection import insertValue

config = ConfigParser()
config.read('static/preferences.ini')
ARD_UDP_IP_SEND = config.get('rpiclient', 'ip')
ARD_UDP_PORT_SEND = config.get('rpiclient', 'port')
ARD_UDP_IP_RECEIVE = config.get('rpiserver', 'ip')
ARD_UDP_PORT_RECEIVE = config.getint('rpiserver', 'port')

# Arduino-Messages
ARD_Start = bytes("070", "ascii")
ARD_Stop = bytes("071", "ascii")
ARD_Kali = bytes("072", "ascii")
ARD_StartReset = bytes("073", "ascii")
ARD_SDRead = bytes("074", "ascii")


def sendStatus():
    """
    sends status to SPS
    :return:
        0: no error
        1: no critical error
        2: error might be critical
        3: System must be stopped
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(glob.WARN_LEVEL, (ARD_UDP_IP_SEND, ARD_UDP_PORT_SEND))
        sock.close()
    except Exception as ex:
        logging.error("arduino_connection.sendStatus(): " + str(ex) +
                      "\n" + traceback.format_exc())


def resetWarnLevel():
    glob.WARN_LEVEL = 0
    logging.info("sps_connection.resetWarnLevel() + \n ###############################################################")


class MyUDPRequestHandler(socketserver.DatagramRequestHandler):
    def handle(self):
        message = self.rfile.readline().strip().decode('UTF-8')
        if "STAT" in message:
            self.readStatus(message)
        if "VALUE" in message:
            typeDataSplit = message.split(";")
            data = {
                "index": int(typeDataSplit[1]),
                "time": datetime.strptime(typeDataSplit[2], '%Y-%m-%d %H:%M:%S.%f'),
                "temp1": float(typeDataSplit[3]),
                "temp2": float(typeDataSplit[4]),
                "temp3": float(typeDataSplit[5]),
                "temp4": float(typeDataSplit[6])
            }
            insertValue(data)
            VALUES.append(data)

    def readStatus(self, message):
        if "WL" in message:
            sendStatus()
        elif "RL" in message:
            resetWarnLevel()


# This class provides a multithreaded UDP server that can receive messages sent to the defined ip and port
class UDPServer(threading.Thread):
    server_address = (ARD_UDP_IP_RECEIVE, ARD_UDP_PORT_RECEIVE)
    udp_server_object = None

    def run(self):
        try:
            self.udp_server_object = socketserver.ThreadingUDPServer(self.server_address, MyUDPRequestHandler)
            self.udp_server_object.serve_forever()
        except Exception as ex:
            glob.setWarnLevel(3)
            logging.error("UDPServer.run(): " + str(ex) + "\n" + traceback.format_exc())

    def stop(self):
        try:
            self.udp_server_object.shutdown()
        except Exception as ex:
            logging.error("UDPServer.stop(): " + str(ex) + "\n" + traceback.format_exc())


class SUDPServer:
    __server: socketserver.ThreadingUDPServer = None

    @staticmethod
    def start_server():
        if SUDPServer.__server is None:
            SUDPServer()
            SUDPServer.__server.start()

    @staticmethod
    def stop_server():
        if SUDPServer.__server is not None:
            SUDPServer.__server.stop()
            SUDPServer.__server = None

    def __init__(self):
        if SUDPServer.__server is not None:
            raise Exception("Class is already initialized")
        SUDPServer.__server = UDPServer()
