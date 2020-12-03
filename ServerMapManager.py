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

authServer

path_rooms = "/home/loren/Documents/Sistemas Distribuidos/SSDD-Selas/Server/rooms/"
path_authors=path_rooms + "Authors.json"

class RoomI(IceGauntlet.RoomManager):

    def publish(self, token, roomData, current=None):
        proxy = server.communicator().stringToProxy(authServer)
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        if not authent:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
        if authent.isValid(token):
            datos=json.loads(roomData)
            path_room=path_rooms + (datos['room'])


            if path.exists(path_room):
                raise IceGauntlet.RoomAlreadyExists


            if not path.exists(path_authors):
                f = open(path_authors, "w")
                ini = {'mapas': [{"token":"MapManager","roomPath":path_authors}]}
                json.dump(ini,f)
                f.close()

            fAuthors = open(path_authors, "r")
            Authors = json.loads(fAuthors.read())
            fAuthors.close()

            mapas = Authors['mapas']
            entry= {'token':token, 'roomPath': path_room}
            mapas.append(entry)

            fAuthors = open(path_authors, "w")
            json.dump(Authors,fAuthors)

            froom = open(path_room, "w")
            froom.write(roomData)
            froom.close()

            return None
        raise IceGauntlet.Unauthorized
    
    def remove(self, token, roomName, current=None):
        proxy = server.communicator().stringToProxy(authServer)
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        if not authent:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
        if authent.isValid(token):
            if path.exists(path_rooms + roomName):
                fAuthors = open(path_authors, "r")
                Authors = json.loads(fAuthors.read())
                for i in range(len(Authors['mapas'])):
                    aux=str(Authors['mapas'][i])
                    linea=json.loads(aux.replace("'",'"'))
                    if linea['token']==token
                        del (Authors['mapas'][i])
                        remove(path_rooms + roomName)
                        fAuthors = open(path_authors, "w")
                        json.dump(Authors,fAuthors)
                        return None
            raise IceGauntlet.RoomNotExists
        raise IceGauntlet.Unauthorized

class Server(Ice.Application):
    def run(self, argv):
        if not len(argv)==2:
            print("use: ./run_map_server --Ice.Config=Server.config <servidor autenticación>")
            sys.exit(server.main(sys.argv))
        authServer=argv[1]
        broker = self.communicator()
        servant = RoomI()

        adapter = broker.createObjectAdapter("MapAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("map1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))