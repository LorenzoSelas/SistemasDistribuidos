#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('IceGauntlet.ice')
import Gauntlet

import random
import os
from os import remove
from os import path
import json

EXIT_OK = 0
EXIT_ERROR = 1

path_rooms = "/home/loren/Documents/Sistemas Distribuidos/Entregable1/Server/rooms/"

def auth_server_pid():
    '''
    Search for a running auth_server and get PID
    '''
    for proc in psutil.process_iter():
        if proc.name().startswith('python3'):
            for arg in proc.cmdline():
                if arg.startswith('./'):
                    arg = arg[2:]
                if arg == 'auth_server':
                    return proc.pid
    return None

class RoomI(Gauntlet.MapManagement):
    
    def __init__(self, name):
        self.name = name

    def getroom(self, current=None):
        fmap = random.choice(os.listdir(path_rooms))
        map = open(path_rooms + fmap)
        print(map)
        sys.stdout.flush()
        return map.read()
    
    def publish(self, token, roomData):
        server_pid = auth_server_pid()
        if not server_pid:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
        if server.pid.isValid(token):
            file = open(path_rooms + "t.json","w")
            file.write(roomData)
            room = json.load(path_rooms + "t.json")
            if path.exists(path_rooms + room['room']):
                raise RoomAlreadyExists
            froom = open(path_rooms + room['room'])
            froom.write(roomData)
            return None
        raise Unauthorized
    
    def remove(self, token, roomName):
        server_pid = auth_server_pid()
        if not server_pid:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
        if server.pid.isValid(token):
            if path.exists(path_rooms + roomName):
                remove(path_rooms + roomName)
                return None
            raise RoomNotExists
        raise Unauthorized


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        properties = broker.getProperties()
        servant = RoomI(properties.getProperty('Ice.ProgramName'))

        adapter = broker.createObjectAdapter("RoomAdapter")
        id_ = properties.getProperty('Identity')
        proxy = adapter.add(servant, broker.stringToIdentity(id_))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))
