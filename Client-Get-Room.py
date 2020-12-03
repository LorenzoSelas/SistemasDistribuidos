#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        room = IceGauntlet.DungeonPrx.checkedCast(proxy)

        if not room:
            raise RuntimeError('Invalid proxy')

        print(room.getRoom())

        return 0


sys.exit(Client().main(sys.argv))
