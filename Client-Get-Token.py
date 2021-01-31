#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getpass
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):

        proxy = self.communicator().stringToProxy(argv[2])
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)

        if not authent:
            raise RuntimeError('Invalid proxy')
        pas = getpass.getpass("Enter password:")
        try:
            print(authent.getNewToken(argv[1],pas))
        except:
            print("error")
            return 1

        return 0


sys.exit(Client().main(sys.argv))
