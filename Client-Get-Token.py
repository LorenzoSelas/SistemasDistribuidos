#!/usr/bin/python3
# -*- coding: utf-8 -*-

import getpass
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class Client(Ice.Application):
    def run(self, argv):
        if not len(argv)==3:
            print("use: ./Client-Get-Token --Ice.Config=Server.config <user> <servidor autenticación>")
            return 0

        proxy = self.communicator().stringToProxy(argv[2])
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)

        if not authent:
            raise RuntimeError('Invalid proxy')
        
        p = getpass.getpass('Enter password:')
        token = authent.getNewToken(argv[1],p)

        print("El token es:" + token)

        tok = open("token.txt", "w")
        tok.write(token)

        return 0


sys.exit(Client().main(sys.argv))
