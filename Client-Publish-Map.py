#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):
        if not len(argv)==4:
            print("use: ./run_map_server --Ice.Config=Server.config <proxy servicio mapas> <token> <archivo mapa>")
            sys.exit(server.main(sys.argv))
        
        proxy = self.communicator().stringToProxy(argv[1])
        token = argv[2]
        archivo = argv[3]
        
        data = open(archivo, "r")

        manager = IceGauntlet.RoomManagerPrx.checkedCast(proxy)

        if not manager:
            raise RuntimeError('Invalid proxy')
        
        proxy = self.communicator().stringToProxy("auth1 -t -e 1.1 @ AuthAdapter1")
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        manager.publish(token, data)

        return 0


sys.exit(Client().main(sys.argv))
