#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import sys
import Ice
import IceStorm
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
from icegauntlettool import filter_map_objects
from icegauntlettool import get_map_objects
from icegauntlettool import search_adjacent_door


import random
import os
from os import remove
from os import path
import json
import uuid


TOPIC_NAME_ROOMMANAGER = "RoomManagerSyncChannel"

EXIT_OK = 0
EXIT_ERROR = 1

PATH_ROOMS = "Server/rooms/"
PATH_ADMIN = "Server/Administrar/"
PATH_AUTHORS = PATH_ADMIN + "Authors.json"

class DungeonArea(IceGauntlet.DungeonArea):
    def __init__(self, mapName, DungeonAreaAdapter, DungeonAreaSyncAdapter, current=None):
        self.mapName = mapName
        self.eventChannel = str(uuid.uuid1)
        self.DungeonAreaSyncAdapter = DungeonAreaSyncAdapter
        self.DungeonAreaAdapter = DungeonAreaAdapter
        self.NextDungeonArea = None
        self.map = open(PATH_ROOMS + mapName)
        self.mapData = self.map.read()
        self.actors = []
        self.items = []
        self.mapWalls = filter_map_objects(self.mapData)
        self.id_count = 0
        for o in get_map_objects(self.mapData):
            self.items.append((self.id_count,o[0],o[1]))
            self.id_count += 1

        self.DungeonAreaSyncServant = DungeonAreaSync(self)

        SyncSubscriber = self.DungeonAreaSyncAdapter.addWithUUID(self.DungeonAreaSyncServant)
        
        topic_mgr = server.get_topic_manager()
        qos ={}
        if not topic_mgr:
            return 2
        
        try:
            topic = topic_mgr.retrieve(self.eventChannel)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(self.eventChannel)
        
        publisher = topic.subscribeAndGetPublisher(qos, SyncSubscriber)

    def addActor(self, actor_id, actor, current=None):
        self.actors.append(actor_id, actor)
    
    def deleteActor(self, actor, current=None):
        self.actors.remove(actor)

    def deleteItem(self, item, current=None):
        self.items.remove(item)

    def getEventChannel(self, current=None):
        return self.eventChannel

    def getMap(self, current=None):
        return self.mapWalls

    def getActors(self, current=None):
        return self.actors

    def getItems(self, current=None):
        return self.items

    def getNextArea(self, current=None):
        if self.NextDungeonArea == None:
            proxy = server.communicator().stringToProxy('map')
            room = IceGauntlet.RoomManagerPrx.checkedCast(proxy)

            if not room:
                raise RuntimeError('Invalid proxy')

            avaRooms = room.availableRooms()
            fmap = random.choice(avaRooms)
            map = open(path_rooms + fmap)
            newDungeonArea = DungeonArea(map.read())

            proxy = self.DungeonAreaAdapter.addWithUUID(newDungeonArea)
            self.NextDungeonArea = IceGauntlet.DungeonAreaPrx.checkedCast(proxy)
        return self.NextDungeonArea


class DungeonAreaSync(IceGauntlet.DungeonAreaSync):
    def __init__(self, padre, current=None):
        self.padre = padre

    def fireEvent(self, event, senderId, current=None):
        evento = pickle.loads(event)
        print(senderId)
        print("-")
        print(event)
        if(evento[0]=="spawn_actor"):
            self.padre.addActor(evento[1],evento[2])
            return None
        if(evento[0]=="kill_object"):
            objects = self.padre.getItems()
            for ob in objects:
                if evento[1] == ob[0]:
                    self.padre.deleteItem(ob)
                    return None
            actors = self.padre.getActors()
            for ac in actors:
                if evento[1] == ac[0]:
                    self.padre.deleteActor(ac)
                    return None
        if(evento[0]=="open_door"):
            position = []
            for obj in self.padre.getItems():
                if obj[0] == evento[1]:
                    position = obj[2]
            adjacentobjects = search_adjacent_door(self.padre.getObjects(), position, None)
            for ob in adjacentobjects:
                for it in self.padre.getItems():
                    if ob == it[0]:
                        self.padre.deleteItem(it)

class Dungeon(IceGauntlet.Dungeon):
    def __init__(self, DungeonAreaAdapter, DungeonAreaSyncAdapter, current=None):
        self.DungeonAreaAdapter = DungeonAreaAdapter
        self.DungeonAreaSyncAdapter = DungeonAreaSyncAdapter
        self.IniMap = "test room"
        self.Dungeon = None

    def getEntrance(self, current=None):
        if self.Dungeon == None:
            new_servant = DungeonArea(self.IniMap, self.DungeonAreaAdapter, self.DungeonAreaSyncAdapter)
            
            proxy = self.DungeonAreaAdapter.addWithUUID(new_servant)
            self.Dungeon = IceGauntlet.DungeonAreaPrx.checkedCast(proxy)
        return self.Dungeon

class RoomSync(IceGauntlet.RoomManagerSync):
    def __init__(self, Manager, ManagerId):
        self.MapManager = Manager
        self.ManagerId = ManagerId
        self._active_servers_ = set()
        self.Servidores = {'servers':[{"Manager":self.MapManager,"id":self.ManagerId}]}
        topic_mgr = server.get_topic_manager()
        if not topic_mgr:
            print('Invalid proxy')
            return 2

        try:
            topic = topic_mgr.retrieve(TOPIC_NAME_ROOMMANAGER)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(TOPIC_NAME_ROOMMANAGER)

        publisher = topic.getPublisher()
        helloer = IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher)
        
        helloer.hello(self.MapManager,self.ManagerId)
        
    def hello(self, MapManager, ManId, current=None):
        if not ManId == self.ManagerId:
            if ManId not in self._active_servers_:
                servidor={"Manager":MapManager,"id":ManId}
                self._active_servers_.add(ManId)
                self.Servidores['servers'].append(servidor)
        topic_mgr = server.get_topic_manager()
        if not topic_mgr:
            return 2
            
        try:
            topic = topic_mgr.retrieve(TOPIC_NAME_ROOMMANAGER)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(TOPIC_NAME_ROOMMANAGER)

        publisher = topic.getPublisher()
        announcer = IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher)
        announcer.announce(self.MapManager, self.ManagerId)

    def announce(self, MapManager, ManId, current=None):
        if not ManId == self.ManagerId:
            if ManId not in self._active_servers_:
                servidor={"Manager":MapManager,"id":ManId}
                self._active_servers_.add(ManId)
                self.Servidores['servers'].append(servidor)
            
            rooms = MapManager.availableRooms()
            for room in rooms:
                if not path.exists(PATH_ROOMS + room):
                    roomData = json.loads(MapManager.getRoom(room))
                    froom = open(path_room, "w")
                    froom.write(datos.dump)
                    froom.close()
    
    def newRoom(self, roomName, ManId, current=None):
        if not ManId == self.ManagerId:
            servidor = None
            for i in range(len(self.Servidores['servers'])):
                print(str(self.Servidores['servers'][i]['id']) +"----" + ManId)
                if self.Servidores['servers'][i]['id'] == ManId: 
                    servidor = self.Servidores['servers'][i]['Manager']
                    break

            roomData = servidor.getRoom(roomName)
            datos = json.loads(roomData)
            path_room = PATH_ROOMS + (datos['room'])
            froom = open(path_room, "w")
            froom.write(roomData)
            froom.close()
    
    def removedRoom(self, roomName, current=None):
        try:
            remove(PATH_ROOMS + roomName)
        except:
            None


class RoomI(IceGauntlet.RoomManager):
    def __init__(self, ser, name, id):
        self.authServer = ser
        self.name = name
        self.id = id

    def availableRooms(self, current=None):
        fmap = os.listdir(PATH_ROOMS)
        return fmap

    def getRoom(self, roomName, current=None):
        try:
            map = open(PATH_ROOMS + roomName)
            return map.read()
        except:
            raise IceGauntlet.RoomNotExists

    def publish(self, token, roomData, current=None):
        proxy = server.communicator().stringToProxy(self.authServer)
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        if not authent:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
        try:
            owner = authent.getOwner(token)
            datos = json.loads(roomData)
            datos['owner']=owner
            path_room = PATH_ROOMS + (datos['room'])

            if path.exists(path_room):
                raise IceGauntlet.RoomAlreadyExists

            with open(path_room, 'w') as content:
                json.dump(datos, content, sort_keys=True)
        except IceGauntlet.RoomAlreadyExists:
            raise IceGauntlet.RoomAlreadyExists
        except:
            raise IceGauntlet.Unauthorized
        
        topic_mgr = server.get_topic_manager()
        if not topic_mgr:
            return 2
        try:
            topic = topic_mgr.retrieve(TOPIC_NAME_ROOMMANAGER)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(TOPIC_NAME_ROOMMANAGER)

        publisher = topic.getPublisher()
        pubsher = IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher)
        pubsher.newRoom(datos['room'], self.id)

        return None
    
    def remove(self, token, roomName, current=None):
        proxy = server.communicator().stringToProxy(self.authServer)
        authent = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        if not authent:
            print('ERROR: auth server process not found. Is the server running?')
            return EXIT_ERROR
        if path.exists(PATH_ROOMS + roomName):
            try:
                owner = authent.getOwner(token)
                froom = open(PATH_ROOMS+roomName, "r")
                room = json.loads(froom.read())

                if room['owner']==owner:
                    remove(PATH_ROOMS + roomName)
                    
                topic_mgr = server.get_topic_manager()
                if not topic_mgr:
                    return 2

                try:
                    topic = topic_mgr.retrieve(TOPIC_NAME_ROOMMANAGER)
                except IceStorm.NoSuchTopic:
                    topic = topic_mgr.create(TOPIC_NAME_ROOMMANAGER)
                    
                publisher = topic.getPublisher()
                remover = IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher)
                remover.removedRoom(roomName)
                return None

            except:
                raise IceGauntlet.Unauthorized
        else:
            raise IceGauntlet.RoomNotExists


class Server(Ice.Application):

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None

        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def run(self, argv):
        broker = self.communicator()
        properties = broker.getProperties()

        DungeonAreaSyncAdapter = broker.createObjectAdapter("DungeonAreaSyncAdapter")
        DungeonAreaAdapter = broker.createObjectAdapter("DungeonAreaAdapter")

        idMap = properties.getProperty('Identity')
        idMapAdapter = properties.getProperty('IdentityMapAdapter')
        servantRoomManager = RoomI("default", properties.getProperty('Ice.ProgramName'),idMapAdapter)
        MapAdapter = broker.createObjectAdapter("MapAdapter")
        proxyMap = MapAdapter.add(servantRoomManager,broker.stringToIdentity(idMap))
        proxyMapAdapter = MapAdapter.add(servantRoomManager,broker.stringToIdentity(idMapAdapter))

        servantDungeon = Dungeon(DungeonAreaAdapter, DungeonAreaSyncAdapter)
        idDungeonAdapter = properties.getProperty('IdentityDungeonAdapter')
        DungeonAdapter = broker.createObjectAdapter("DungeonAdapter")
        proxyDungeon = DungeonAdapter.add(servantDungeon,broker.stringToIdentity(idDungeonAdapter))

        proxy = broker.stringToProxy(idMapAdapter)
        servantRoomSync = RoomSync(IceGauntlet.RoomManagerPrx.checkedCast(proxy),idMapAdapter)
        RoomSyncAdapter = broker.createObjectAdapter("RoomSyncAdapter")
        idRoomSyncAdapter = properties.getProperty('IdentityRoomSyncAdapter')
        SyncSubscriber = RoomSyncAdapter.add(servantRoomSync, broker.stringToIdentity(idRoomSyncAdapter))

        topic_mgr = server.get_topic_manager()
        qos ={}
        if not topic_mgr:
            return 2
        
        try:
            topic = topic_mgr.retrieve(TOPIC_NAME_ROOMMANAGER)
        except IceStorm.NoSuchTopic:
            topic = topic_mgr.create(TOPIC_NAME_ROOMMANAGER)
        
        publisher = topic.subscribeAndGetPublisher(qos, SyncSubscriber)

        print('"{}"'.format(proxyMap), flush=True)
        print(proxyDungeon)

        MapAdapter.activate()
        DungeonAdapter.activate()
        DungeonAreaSyncAdapter.activate()
        DungeonAreaAdapter.activate()
        RoomSyncAdapter.activate()
        broker.waitForShutdown()
        topic.unsubscribe(publisher)
        self.shutdownOnInterrupt()
        return 0


server = Server()
sys.exit(server.main(sys.argv))