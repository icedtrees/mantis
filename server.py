"""
A UDP server designed to be run on the robot (Raspberry Pi or similar)
and uses the sample interface.py system
"""

import SocketServer
import interface


class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # print "{} wrote:".format(self.client_address[0])
        # print data
        socket.sendto(data.upper(), self.client_address)
        interface.execute_command(data)

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
