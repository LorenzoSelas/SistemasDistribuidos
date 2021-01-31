#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getpass
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):

        proxy = self.communicator().stringToProxy(argv[1])
        manager = IceGauntlet.RoomManagerPrx.checkedCast(proxy)

        if not manager:
            raise RuntimeError('Invalid proxy')
        
        data = open(argv[3], "r")

        manager.publish(argv[2], data.read())

        return 0


sys.exit(Client().main(sys.argv))
