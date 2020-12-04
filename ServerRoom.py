#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

import random
import os
from os import remove
from os import path
import json

EXIT_OK = 0
EXIT_ERROR = 1

path_rooms = "/home/loren/Documents/Sistemas Distribuidos/SSDD-Selas/Server/rooms/"

class DungeonI(IceGauntlet.Dungeon):

    def getRoom(self, current=None):
        if not os.listdir(path_rooms):
            raise IceGauntlet.RoomNotExists
        fmap = random.choice(os.listdir(path_rooms))
        map = open(path_rooms + fmap)
        sys.stdout.flush()
        return map.read()


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = DungeonI()

        adapter = broker.createObjectAdapter("RoomAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("room1"))

        print('"{}"'.format(proxy), flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))