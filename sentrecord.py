#!/usr/bin/env python3
import sqlite3
import threading as th
from requests import post
import os.path as _path
import time

headers = {'Content-type':'application/x-www-form-urlencoded','Accept':'text/plain'}
tstamp_path = '/home/pi/tutorial/timestamp'
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = dict_factory
        return conn
    except Exception as e:
        print('Error!!:',e)
        return None

def dict_factory(cursor, row):
    d = {}
    tmp = [0,0]
    for idx,col in enumerate(cursor.description):
        if col[0] == 'alt':
            d['altitude'] = row[idx]
        elif col[0] == 'lat':
            tmp[1] = row[idx]
        elif col[0] == 'lon':
            tmp[0] = row[idx]
        else:
            d[col[0]] = row[idx]
        d['hori_position'] = tmp
    return d

def get_records(conn,start,stop):
    cur = conn.cursor()
    query = "SELECT * FROM ADSB WHERE datetime BETWEEN %s AND %s LIMIT 10000;"%(start,stop)
    print(query)
    cur.execute(query)
    rows = cur.fetchall()
    return rows

def get_first_records(conn):
    cur = conn.cursor()
    query = "SELECT datetime FROM ADSB LIMIT 1;"
    cur.execute(query)
    first_row = cur.fetchone()
    return first_row['datetime']

def sent_record(record,ttl=3,t=10):
    r = None
    try:
        r = post('http://gisavia.gistda.or.th:8080/insertfeatures/adsbdata',data=record,headers=headers,timeout=3)
        print(r)
    except:
        if ttl>0:
            sent_record(record,ttl=ttl-1)
    return r

def sent_records(data):
    count=0
    num_data = len(data)
    s = time.time()
    if len(data)==0:
        return None
    for i,d in enumerate(data):
        try:
            print(i)
            r = sent_record(d,ttl=1)
            if r == None:
                count+=1
            timestamp = d['datetime']
            #input()
        except Exception as e:
            print("Error",e,":Can't upload record")
            with open(tstamp_path,'w') as f:
                f.write(str(timestamp))
            return timestamp
    print(count)
    timestamp = timestamp+0.000001
    with open(tstamp_path,'w') as f:
        f.write(str(timestamp))
    return timestamp

def main():
    database = "/home/pi/tutorial/test.db"
    num_thread = 4
    conn = create_connection(database)
    if(not _path.isfile(tstamp_path)):
        f = open(tstamp_path,'w')
        f.write(str(get_first_records(conn)))
        f.close()
    while True:
        threads = []
        with open(tstamp_path,'r') as f:
            start = f.read()
            stop = time.time()
            #stop = 1513929738
        #refresh data
        with conn:
            datas = get_records(conn,start,str(stop))
            batch = (len(datas)//num_thread)+1
            
            for i in range(num_thread):
                threads.append(th.Thread(target=sent_records,args=(datas[batch*i:batch*(i+1)],)))
            for i in threads:
                i.start()
            for i in threads:
                i.join()
            

if __name__ == '__main__':
    main()
