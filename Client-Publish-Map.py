#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):
        if not len(argv)==4:
            print("use: ./Client-Publish-Map.py --Ice.Config=Server.config <proxy servicio mapas> <token> <archivo mapa>")
            return 0
        
        proxy = self.communicator().stringToProxy(argv[1])
        manager = IceGauntlet.RoomManagerPrx.checkedCast(proxy)

        if not manager:
            raise RuntimeError('Invalid proxy')
        
        token = argv[2]
        archivo = argv[3]
        
        data = open(archivo, "r")

        manager.publish(token, data.read())

        return 0


sys.exit(Client().main(sys.argv))