#!/usr/bin/env python3

import json
import os
from time import sleep
import sqlite3
from sqlite3 import Error
from datetime import datetime
import time
import sys
from flightdata import FlightData

DATABASE_PATH = '/home/pi/tutorial/test.db'

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except:
        print(sys.exc_info())
        return None

def create_record(conn, aircraft):
    sql = ''' INSERT INTO ADSB(ihex, icao, flight_id, lat, lon, alt,
              heading, hor_vel, ver_vel, datetime, date, time)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'''
    try:
        cur = conn.cursor()
        cur.execute(sql, aircraft)
        conn.commit()
    except:
        print('Error on Inser Record:',sys.exc_info())

#test    
if __name__ == "__main__":
    #create FlightData object
    myflights = FlightData()
    conn = create_connection(DATABASE_PATH)
    try:
        while True:
            dt = datetime.now()
            d = '{:%Y-%m-%d}'.format(dt)
            t = '{:%H:%M:%S}'.format(dt)
            timestamp = time.time()
            #loop through each aircraft found
            for aircraft in myflights.aircraft:
                #print the aircraft's data
                print('Time:',t)
                print('hex:',aircraft.hex)
                print('flight ID:',aircraft.flight)
                print('latitude:',aircraft.lat)
                print('longitude:',aircraft.lon)
                print('altitude:',aircraft.altitude)
                print('vertical rate:',aircraft.vert_rate)
                print('speed:',aircraft.speed)
                record = (aircraft.hex,aircraft.hex,aircraft.flight,aircraft.lat,\
                          aircraft.lon,aircraft.altitude,aircraft.heading,\
                          aircraft.speed,aircraft.vert_rate,timestamp,d,t)
                print('record:',record)
                create_record(conn,record)
            sleep(1)

            #refresh the flight data
            myflights.refresh()
            #os.system('clear')
    except KeyboardInterrupt:
        print('Exit Connection')
        conn.close()
        

