#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
        
        proxy = self.communicator().stringToProxy("auth1 -t -e 1.1 @ AuthAdapter1")
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        manager.remove("BKcYoLBvML7jNrBOHyAGhgSozpU7JB68URMvIXVc","loren room.json")

        return 0


sys.exit(Client().main(sys.argv))
