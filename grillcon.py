#!/usr/bin/env python

#grillcon
#Chris Pangburn - 2016

from controller import Controller
from rest import BottleServer
import socket

if __name__ == "__main__":


    def internet(host="8.8.8.8", port=53, timeout=3):
        """
      Host: 8.8.8.8 (google-public-dns-a.google.com)
      OpenPort: 53/tcp
      Service: domain (DNS/TCP)
      """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        print ex.message
        return False

    myController = Controller()
    #moved the start call to the init
    #myController.start()

    myWebApp = BottleServer()
    myWebApp.run(host='0.0.0.0', port=8080)
    
    
