"""
A UDP server designed to be run on the robot (Raspberry Pi or similar)
and uses the sample interface.py system
"""

import sys
import SocketServer

import interface


class MyUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        command = self.request[0].strip()
        interface.execute_command(command)

if __name__ == "__main__":
    try:
        host, port = "0.0.0.0", int(sys.argv[1])
    except IndexError:
        print("Usage: {} port".format(sys.argv[0]))
        exit(1)
    server = SocketServer.UDPServer((host, port), MyUDPHandler)
    server.serve_forever()
