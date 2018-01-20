#!/usr/bin/env python

#grillcon
#Chris Pangburn - 2016

from controller import Controller
from rest import BottleServer

if __name__ == "__main__":

    myController = Controller()
    myController.start()

    myWebApp = BottleServer()
    myWebApp.run(host='localhost', port=8080)
    
    
