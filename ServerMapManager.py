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


path_rooms = "Server/rooms/"
path_Admin = "Server/Administrar/"
path_authors=path_Admin + "Authors.json"

class RoomI(IceGauntlet.RoomManager):
    def __init__(self, ser):
        self.authServer=ser

    def publish(self, token, roomData, current=None):
        proxy = server.communicator().stringToProxy(self.authServer)
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
        proxy = server.communicator().stringToProxy(self.authServer)
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
                    if linea['token']==token:
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
            print("use: ./ServerMapManager.py --Ice.Config=Server.config <servidor autenticación>")
            return 0
        broker = self.communicator()
        servant = RoomI(argv[1])

        adapter = broker.createObjectAdapter("MapAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("map1"))

        proxyauth = server.communicator().stringToProxy(argv[1])
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxyauth)
        if not authent:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
            
        print('"{}"'.format(proxy), flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
