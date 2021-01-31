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
        try:
            manager.remove(argv[2], argv[3])
        except:
            print("error")
            return 1

        return 0


sys.exit(Client().main(sys.argv))
