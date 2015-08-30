#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2015 R.Rauer                             software@rrauer.de
#########################################################################
#  This file is part of SmartHome.py.    http://mknx.github.io/smarthome/
#
#  SmartHome.py is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHome.py is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import logging
import os

# debugging
#import pydevd

logger = logging.getLogger('')

class Rpi1Wire():
    #pydevd.settrace('192.168.178.25', port=12000, stdoutToServer=True, stderrToServer=True)
    #pydevd.settrace('192.168.178.69', port=12000, stdoutToServer=True, stderrToServer=True)


    def __init__(self, smarthome, dirname="/sys/bus/w1/devices",cycle = 120):
        #pydevd.settrace('192.168.178.25', port=12000, stdoutToServer=True, stderrToServer=True)
        logger.info('Init rpi1wire')
        self._sh = smarthome
        self.dirname = dirname
        self.cycle = cycle
        self.sensors = {}
        self._sensordaten = {}
        self.values = {}
        self.update = False
        self.get_sensors()
        self.anz_sensors = len(self.sensors)
        logger.info("rpi1wire find {0} sensors".format(self.anz_sensors))
        logger.info(self.sensors)
        self._sh.scheduler.add('rpi1wire', self.update_values, prio=3, cycle=self.cycle)



    def run(self):
        self.alive = True
        self.update_values()
        self.update_basics()

    def update_basics(self):
        anz = self._sh.return_item("rpi1wire.sensors")
        ids = self._sh.return_item("rpi1wire.sensor_list")
        if anz != None:
            anz(int(self.anz_sensors),'rpi1wire')
            logger.debug("rpi1wire-item sensors value = {0}".format(self.anz_sensors))
        if ids != None:
            ids(str(self.sensors),'rpi1wire')
            logger.debug("rpi1wire-item sensor_list value = {0}".format(self.sensors))

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if 'rpi1wire_update' in item.conf:
            ad=item.conf['rpi1wire_update']
            return self.update_item
        if 'rpi1wire_id' not in item.conf:
            if 'rpi1wire_name' not in item.conf:
                return None
        if 'rpi1wire_unit' not in item.conf:
            logger.warning("rpi1wire_unit for {0} not defined".format(item.id()))
            return None
        #pydevd.settrace('192.168.178.25', port=12000, stdoutToServer=True, stderrToServer=True)
        #pydevd.settrace('192.168.178.69', port=12000, stdoutToServer=True, stderrToServer=True)
        not_found = False
        if 'rpi1wire_id'in item.conf:
            addr = item.conf['rpi1wire_id']
            try:
                for sn, sid in self.sensors.items():
                    if sid == item.conf['rpi1wire_id']:
                        name = sn
                        break
            except:
                logger.warning("Sensor {0} Hardware not found".format(item.conf['rpi1wire_id']))
                not_found = True
        else:
            if 'rpi1wire_name'in item.conf:
                name = item.conf['rpi1wire_name']
                try:
              	    addr = self.sensors[item.conf['rpi1wire_name']]
                except:
                    logger.warning("Sensor {0} Hardware not found".format(item.conf['rpi1wire_name']))
                    not_found = True
        if not_found == False:
            #self._sensordaten[addr] = {'item': item, 'name': name}
            self._sensordaten[addr]['item'] = item
            logger.info("{0} rpi1wire-items registriert".format(len(self._sensordaten)))

    def parse_logic(self, logic):
        pass

    def update_item(self, item, caller=None, source=None, dest=None):
        #pydevd.settrace('192.168.178.25', port=12000, stdoutToServer=True, stderrToServer=True)
        if self.update == True:
            return None
        if 'rpi1wire_update' in item.conf:
            logger.info("rpi1wire_update wurde angefordert")
            self.update_sensors()
            return None
        if caller != 'plugin':
            logger.info("update item: {0}".format(item.id()))

    def update_values(self):
         for sensor in self.sensors:
            id = self.sensors[sensor]
            value = self.getvalue(id)
            #if value != 99999:
            text = sensor +"=" + sensor[0] +": " + str(round(value/float(1000),1)) + " (" + str(value)+")"
            logger.debug(text)
            self.values[sensor] = round(value/float(1000),1)
            try:
                rpix = self._sensordaten[id]
                temp = rpix['item']
                temp(round(value/float(1000),1), "rpi1wire")
                self._sensordaten[id]['value'] = round(value/float(1000),1)
            except:
                logger.info("sensor {0} has no item".format(id))
            #print("Temperatursensor ",sensor,": ", round(value/float(1000),1), "(",value,")",sep=" ")
                 
    def get_sensors(self):
        #pydevd.settrace('192.168.178.25', port=12000, stdoutToServer=True, stderrToServer=True)
        objects = self.folder_objects(self.dirname)
        i=1
        for sensor in objects:
            if 'w1_bus' in sensor:
                continue
            typ = sensor.rsplit("-",1)
            #if typ[0] == "28":
            if typ[0] in ['10', '22', '28']:
                value = self.getvalue(sensor)
                if value == 99999:
                    logger.warning("rpi1wire {0} - has no value".format(sensor))
                else:
                    text = "rpi_temp"+str(i)+"=" + sensor +": " + str(round(value/float(1000),1)) + " (" + str(value)+")"
                    logger.info(text)
                    self.sensors["rpi_temp"+str(i)] = sensor
                    self.values["rpi_temp"+str(i)] = round(value/float(1000),1)
                    self._sensordaten[sensor]= {'name' : "rpi_temp"+str(i), 'value' : round(value/float(1000),1)}
                    #print("Temperatursensor ",sensor,": ", round(value/float(1000),1), "(",value,")",sep=" ")
                    i+=1

    def folder_objects(self, dirname, otype="all"):
        if (os.path.exists(dirname) == False or
            os.path.isdir(dirname) == False or
            os.access(dirname, os.R_OK) == False):
            return False
        else:
            objects = os.listdir(dirname)
            result = []
            for objectname in objects:
                objectpath = dirname + "/" + objectname
                if (otype == "all" or
                    (otype == "dir" and os.path.isdir(objectpath)  == True) or
                    (otype == "file" and os.path.isfile(objectpath) == True) or
                    (otype == "link" and os.path.islink(objectpath) == True)):
                    result.append(objectname)
            result.sort()
            return result


    def getvalue(self, id):
        try:
            mytemp = ''
            filename = 'w1_slave'
            f = open('/' + self.dirname + '/' + id + '/' + filename, 'r')
            line = f.readline() # read 1st line
            crc = line.rsplit(' ',1)
            crc = crc[1].replace('\n', '')
            if crc=='YES':
                line = f.readline() # read 2nd line
                mytemp = line.rsplit('t=',1)
            else:
                logger.warning("rpi1wire {0} - return no value".format(id))
                mytemp = '99999'
            f.close()
            return int(mytemp[1])
        except:
            logger.warning("can not read sensor {}".format(id))
            return 99999

    def update_sensors(self):
        #pydevd.settrace('192.168.178.69', port=12000, stdoutToServer=True, stderrToServer=True)
        self.update = True
        #for a in self.sensors:
        #    del self.sensors[a]
        self.sensors = {}
        self.anz_sensors = 0
        self.get_sensors()
        self.anz_sensors = len(self.sensors)
        self.search_item()
        self.update_basics()
        self.update_values()
        upd = self._sh.return_item("rpi1wire.update")
        if upd != None:
            upd(False,'rpi1wire')
            logger.info("rpi1wire-item update value done, {0} sensors found".format(self.anz_sensors))
        self.update = False

    def search_item(self):
        items = self._sh.return_items()
        for item in items:
            if 'rpi1wire_id'in item.conf:
                addr = item.conf['rpi1wire_id']
                try:
                    for sn, sid in self.sensors.items():
                        if sid == item.conf['rpi1wire_id']:
                            name = sn
                            self._sensordaten[addr]['item'] = item
                            break
                except:
                    logger.warning("Sensor {0} Hardware not found".format(item.conf['rpi1wire_id']))
                    not_found = True
            if 'rpi1wire_name'in item.conf:
                name = item.conf['rpi1wire_name']
                try:
                    addr = self.sensors[item.conf['rpi1wire_name']]
                    self._sensordaten[addr]['item'] = item
                except:
                    logger.warning("Sensor {0} Hardware not found".format(item.conf['rpi1wire_name']))
        logger.info("{0} rpi1wire-items registriert".format(len(self._sensordaten)))