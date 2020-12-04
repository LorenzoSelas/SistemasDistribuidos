#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):
        if not len(argv)==4:
            print("Formato erroneo: ./Client-Delete-Map.py <Server Mapas> <token> <archivo>")
        proxy = self.communicator().stringToProxy(argv[1])
        manager = IceGauntlet.RoomManagerPrx.checkedCast(proxy)

        if not manager:
            raise RuntimeError('Invalid proxy')
        
        manager.remove(argv[2],argv[3])

        return 0


sys.exit(Client().main(sys.argv))
