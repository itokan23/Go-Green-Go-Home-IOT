# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 01:11:01 2016

@author: dgree
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 10:04:13 2016

@author: applejackcherry
"""

#import serial
import PyCmdMessenger
# Import requests and json modules
import requests
import json
import numpy as np
from scipy.sparse import coo_matrix, vstack, hstack
import math 
import scipy as sp
from scipy.sparse import diags
np.set_printoptions(threshold=np.inf)

#START EVERYTHING AT 6PM, ASSUME RESIDENT GONE FROM 8AM to 6PM

import time
import datetime
import pandas as pd
import matplotlib.pylab as plt
import operator 
import sys
from collections import OrderedDict
from random import randrange

base = 'https://api.watttime.org'
network_id = 'local'

charge = [None] * 48
wash_dry = [None] * 24
temp_schedule = [None] * 48

[
    {
        "name": "California Independent System Operator",
        "ba_type": "ISO",
        "url": "https://api.watttime.org/api/v1/balancing_authorities/CAISO/",
        "abbrev": "CAISO",
        "link": "http://oasis.caiso.com/",
        "states": ["CA"],
        "notes": ""
    }
]
#Problem: Only getting certain number of values > Not for full range? 
query1 = {
    'ba': 'CAISO',
    'market': 'DAHR', #CHANGE TO DAHR
    #'page_size':'2',
    'start_at': '2016-10-28T18:00:00', # Put user variable here instead 
    'end_at': '2016-10-29T16:00:00',

}

query2 = {
    'ba': 'CAISO',
    'market': 'RT5M', #CHANGE TO DAHR
    #'page_size':'2',
    'start_at': '2016-10-28T08:00:00', # Put user variable here instead 
    'end_at': '2016-10-29T07:00:00',

}

def YesterdayPredicted():
    time.sleep(2)
    response = requests.get('https://api.watttime.org/api/v1/datapoints/', params=query1, headers={'Authorization': 'Token 8f070e0b3fa08271a1eb0973638c17bcbc8e6ad2'})
    dictionary = json.loads(response.text)  #turn clump of data into a dicionary
    updated = dictionary['results']  #extract results list from dictionary
    
    time1 = [d['timestamp'] for d in updated]  #take out timestamp from long list
    carbon1 = [d['carbon'] for d in updated]  #take out carbon from long list
    new = dict(zip(time1, carbon1))   #Create a new dictionary with just these values
    list_new = [ [k,v] for k, v in new.items() ] #Turn into a list 
    print carbon1
    '''print type(carbon1)
    carbon1.extend([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    print carbon1
    print type(carbon1)'''
    #print list_new
    times = [datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ') for t in time1]
    '''#print times #Remember these are UTC times (7 hours ahead)
    ylim = max(carbon1)+200
    
    plt.plot(times, carbon1)
    plt.xlim([times[-1],times[0]])
    plt.ylim([0,ylim])
    plt.xlabel("Time (UTC)")
    plt.ylabel("Carbon Footprint (lb CO2/MW)")
    plt.legend()
    plt.show()'''
    
    
def YesterdayActual():
    time.sleep(2)
    response = requests.get('https://api.watttime.org/api/v1/datapoints/', params=query2, headers={'Authorization': 'Token 8f070e0b3fa08271a1eb0973638c17bcbc8e6ad2'})
    dictionary = json.loads(response.text)  #turn clump of data into a dicionary
    updated = dictionary['results']  #extract results list from dictionary
    
    time1 = [d['timestamp'] for d in updated]  #take out timestamp from long list
    carbon1 = [d['carbon'] for d in updated]  #take out carbon from long list
    new = dict(zip(time1, carbon1))   #Create a new dictionary with just these values
    list_new = [ [k,v] for k, v in new.items() ] #Turn into a list 
    print carbon1
    #print list_new
    times = [datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ') for t in time1]
    #print times #Remember these are UTC times (7 hours ahead)
    ylim = max(carbon1)+200
    
    plt.plot(times, carbon1)
    plt.xlim([times[-1],times[0]])
    plt.ylim([0,ylim])
    plt.xlabel("Time (UTC)")
    plt.ylabel("Carbon Footprint (lb CO2/MW)")
    plt.legend()
    plt.show()

YesterdayPredicted()
#YesterdayPredicted()

def lp_mainev():
    
    time.sleep(2)
    response = requests.get('https://api.watttime.org/api/v1/datapoints/', params=query1, headers={'Authorization': 'Token 8f070e0b3fa08271a1eb0973638c17bcbc8e6ad2'})
    dictionary = json.loads(response.text)  #turn clump of data into a dicionary
    updated = dictionary['results']  #extract results list from dictionary
    
    time1 = [d['timestamp'] for d in updated]  #take out timestamp from long list
    carbon1 = [d['carbon'] for d in updated]  #take out carbon from long list
    new = dict(zip(time1, carbon1))   #Create a new dictionary with just these values
    list_new = [ [k,v] for k, v in new.items() ] #Turn into a list 
    carbon1.extend([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    carbonfin = [x * 0.001 for x in carbon1]
    
    #Figure out the elements in each matrix 
    #DETERMINING  A1
    a11 = np.eye(24,M=47,k=23)
    a12 =np.eye(24,M=47,k=23)
    nega1 = np.negative(a11)
    a1a = np.vstack([nega1,a12]) 
    a1 = np.matrix(a1a)
    
    #DETERMINING B1
    #Emin
    Emax = 24
    kout = 8 #User specifies number of hours after 6pm that they need charged by (eg if 3 they need charged by 9)
    Pmax = 6.6
    b11 = []
    for k in range (0,24):
        row = []
        Emin = max(0,Emax-(kout - k)*Pmax)
        if Emin <= 24:
            row.append(Emin)
        else:
            row.append(24)
        b11.append(row)
    b1par = np.matrix(b11)
    b1parneg = np.negative(b1par)
    b1part = np.full((24,1),24,dtype=int)
    b1 = np.vstack([b1parneg,b1part])
    
    #DETERMINING  A2
    a31 = np.eye(24,M=47,k=0)
    a32 =np.eye(24,M=47,k=0)
    nega31 = np.negative(a31)
    a2a = np.vstack([nega31,a32])
    a2 = np.matrix(a2a)
    
    #DETERMINING B2
    b31 = np.full((24,1),0,dtype=int)
    b32 = np.full((24,1),6.6,dtype=float)
    b2a = np.vstack([b31,b32])
    b2 = np.matrix(b2a)
    
    #COMBINE ALL A's
    Aa = np.vstack([a1,a2])
    A = np.matrix(Aa).tolist()
    
    #COMBINE ALL B'S
    ba = np.vstack([b1,b2])
    binit = np.matrix(ba).tolist()
    b = [val for sublist in binit for val in sublist]
    
    #DETERMINING E
    t=1
    ediagonals = [[t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]
    ediags = diags(ediagonals,[0,23,24],shape=(23,47)).toarray()
    esingle = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    Ea = np.vstack([ediags,esingle])
    E = np.matrix(Ea).tolist()
    
    #DETERMINING d
    dinit = np.full((24,1),0,dtype=int).tolist()
    d = [val for sublist in dinit for val in sublist]
    
    base = 'http://127.0.0.1:5000'
    endpoint = '/v1/solve/lp'
    address = base + endpoint

    # Set query (i.e. http://url.com/?key=value).
    query = {'api_key':'ce186'}
    # Set header.
    header = {'Content-Type':'application/json'}

    # Formulate LP problem
    c = carbonfin  #[9,5,20,7,3,6,8,2,1,35,4,15,16,17,18,13,8,6,4,3,10,13,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    A = A
    b = b
    E = E
    d = d
    bounds = [["Default",0,"None"]]
    # Set body (also referred to as data or payload). Body is a JSON string.
    payload = {'c':c,'r':0,'A':A,'b':b,'E':E,'d':d,'bounds':bounds}
    body = json.dumps(payload)

    # Form and send request. Set timeout to 2 minutes. Receive response.
    r = requests.request('post', address, data=body, params=query, headers=header, timeout=120 )

    # Text is JSON string. Convert to Python dictionary/list
    #print r.text
    print "LP Solution"
    solution = json.loads( r.text )
    objec = solution['objective']
    print 'GHG Emissions(lb CO2-e):',objec
    values = solution['x']  #Take LP Solution and Make a list of values
    print 'EV Schedule:',values
    global charge
    charge = values
lp_mainev()

def lp_main_washdry():
    
    time.sleep(2)
    response = requests.get('https://api.watttime.org/api/v1/datapoints/', params=query1, headers={'Authorization': 'Token 8f070e0b3fa08271a1eb0973638c17bcbc8e6ad2'})
    dictionary = json.loads(response.text)  #turn clump of data into a dicionary
    updated = dictionary['results']  #extract results list from dictionary
    
    time1 = [d['timestamp'] for d in updated]  #take out timestamp from long list
    carbon2 = [d['carbon'] for d in updated]  #take out carbon from long list   
    
    #DETERMINING E1 (T)
    #Say they need it done by 8AM
    #That means washer needs to start at 6am
    #which is 12 hours after 6pm-subtract 2 from time difference
    wout = 12
    #Make sure it goes once and only once within time constraints
    E11 = np.full((1,wout),1,dtype=int)
    E12 = np.full((1,(23+(23-wout))),0,dtype=int)
    E1a = np.hstack([E11,E12])
    E13 = np.full((1,23),0,dtype=int)
    E14 = np.full((1,wout),1,dtype=int)
    E15 = np.full((1,(23-wout)),0,dtype=int)
    E1b = np.hstack([E13,E14,E15])
    E1 = np.vstack([E1a,E1b]).tolist()
    
    #DETERMINING d1
    d1 = np.full((2,1),1,dtype=int)
    
    #DETERMINING E2
    #Make sure dryer happens after washer
    E2a = np.eye(22,M=23,k=0)
    E2b = np.eye(22,M=23,k=1)
    E2c = np.negative(E2b)
    E2 = np.hstack([E2a,E2c]).tolist()
    
    #DETERMINING D2
    d2 = np.full((22,1),0,dtype=int)
    
    #COMBINING E
    E = np.vstack([E1,E2]).tolist()
    
    #COMBINING d
    dd = np.vstack([d1,d2]).tolist()
    d = [val for sublist in dd for val in sublist]
    
    #carbon2 = [9,5,20,7,3,6,8,2,1,35,4,15,16,17,18,13,8,6,4,3,10,13,16,]
    carbon2a = [x * 0.000255 for x in carbon2] #For washer
    carbon2b = [y * 0.00279 for y in carbon2]  #For dryer
    double = np.hstack([carbon2a,carbon2b]).tolist()

    base = 'http://127.0.0.1:5000'
    endpoint = '/v1/solve/milp'
    address = base + endpoint

    # Set query (i.e. http://url.com/?key=value).
    query = {'api_key':'ce186'}
    # Set header.
    header = {'Content-Type':'application/json'}

    # Formulate LP problem
    c = double  #[9,5,20,7,3,6,8,2,1,35,4,15,16,17,18,13,8,6,4,3,10,13,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    A = []
    b = []
    E = E
    d = d
    #bounds = [["Default",0,1]]
    binary = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45]
    # Set body (also referred to as data or payload). Body is a JSON string.
    payload = {'c':c,'r':0,'A':A,'b':b,'E':E,'d':d,'binary':binary}
    body = json.dumps(payload)

    # Form and send request. Set timeout to 2 minutes. Receive response.
    r = requests.request('post', address, data=body, params=query, headers=header, timeout=120 )

    # Text is JSON string. Convert to Python dictionary/list
    #print r.text
    print "LP Solution"
    solution = json.loads( r.text )
    objec = solution['objective']
    print 'GHG Emissions(lb CO2-e):',objec
    values = solution['x']  #Take LP Solution and Make a list of values
    print 'Wash/Dry Schedule:',values
    global wash_dry
    wash_dry = values

lp_main_washdry()

def lp_maintemp():
    
    time.sleep(2)
    response = requests.get('https://api.watttime.org/api/v1/datapoints/', params=query1, headers={'Authorization': 'Token 8f070e0b3fa08271a1eb0973638c17bcbc8e6ad2'})
    dictionary = json.loads(response.text)  #turn clump of data into a dicionary
    updated = dictionary['results']  #extract results list from dictionary
    
    time1 = [d['timestamp'] for d in updated]  #take out timestamp from long list
    carbon1 = [d['carbon'] for d in updated]  #take out carbon from long list
    new = dict(zip(time1, carbon1))   #Create a new dictionary with just these values
    list_new = [ [k,v] for k, v in new.items() ] #Turn into a list 
    carbon1.extend([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    carbonfin = [x * 0.001 for x in carbon1]
    
    #DETERMINING  A1
    a11 = np.eye(24,M=47,k=23)
    a12 =np.eye(24,M=47,k=23)
    nega1 = np.negative(a11)
    a1a = np.vstack([nega1,a12]) 
    a1 = np.matrix(a1a)
    
    #DETERMINING B1
    #Emin
    templist= ['3','2.5','2.0','1.2','0','2.2','5','10','15','20','30']
    random = int(randrange(0,len(templist)))
    Emax = float(templist[random])
    #Emax = 24
    kout = 23 #Assume has to be done by the time user gets home
    #random = 3
    if random <= 3:
        Pmax = 1.2
        print 'Cooling Energy Needed(kWh):',Emax
    elif random >= 5:
        Pmax = 2.2
        print "Heating Energy Needed(kWh):",Emax
    else:
        print "No Energy Needed Today! :)"
        sys.exit()
    
    b11 = []
    for k in range (0,24):
        row = []
        Emin = max(0,Emax-(kout - k)*Pmax)
        if Emin <= 24:
            row.append(Emin)
        else:
            row.append(24)
        b11.append(row)
    b1par = np.matrix(b11)
    b1parneg = np.negative(b1par)
    b1part = np.full((24,1),24,dtype=int)
    b1 = np.vstack([b1parneg,b1part])
    
    #DETERMINING  A2
    a31 = np.eye(24,M=47,k=0)
    a32 =np.eye(24,M=47,k=0)
    nega31 = np.negative(a31)
    a2a = np.vstack([nega31,a32])
    a2 = np.matrix(a2a)
    
    #DETERMINING B2
    b31 = np.full((24,1),0,dtype=int)
    b32 = np.full((24,1),Pmax,dtype=float)
    b2a = np.vstack([b31,b32])
    b2 = np.matrix(b2a)
    
    #COMBINE ALL A's
    Aa = np.vstack([a1,a2])
    A = np.matrix(Aa).tolist()
    
    #COMBINE ALL B'S
    ba = np.vstack([b1,b2])
    binit = np.matrix(ba).tolist()
    b = [val for sublist in binit for val in sublist]
    
    #DETERMINING E
    t=1
    ediagonals = [[t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,t,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]]
    ediags = diags(ediagonals,[0,23,24],shape=(23,47)).toarray()
    esingle = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    Ea = np.vstack([ediags,esingle])
    E = np.matrix(Ea).tolist()
    
    #DETERMINING d
    dinit = np.full((24,1),0,dtype=int).tolist()
    d = [val for sublist in dinit for val in sublist]
    
    base = 'http://127.0.0.1:5000'
    endpoint = '/v1/solve/lp'
    address = base + endpoint

    # Set query (i.e. http://url.com/?key=value).
    query = {'api_key':'ce186'}
    # Set header.
    header = {'Content-Type':'application/json'}

    # Formulate LP problem
    c = carbonfin  #[9,5,20,7,3,6,8,2,1,35,4,15,16,17,18,13,8,6,4,3,10,13,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    A = A
    b = b
    E = E
    d = d
    bounds = [["Default",0,"None"]]
    # Set body (also referred to as data or payload). Body is a JSON string.
    payload = {'c':c,'r':0,'A':A,'b':b,'E':E,'d':d,'bounds':bounds}
    body = json.dumps(payload)

    # Form and send request. Set timeout to 2 minutes. Receive response.
    r = requests.request('post', address, data=body, params=query, headers=header, timeout=120 )

    # Text is JSON string. Convert to Python dictionary/list
    #print r.text
    print "LP Solution"
    solution = json.loads( r.text )
    objec = solution['objective']
    print 'GHG Emissions(lb CO2-e):',objec
    values = solution['x']  #Take LP Solution and Make a list of values
    print 'Temp Schedule:',values
    global temp_schedule
    temp_schedule = values
lp_maintemp()

def send_main():

    serial_port_name = "COM6"
    connected = False
    ser = serial.Serial(serial_port_name, 9600)
    time.sleep(2) #to allow initialize before sending data
    for x in range(0, 48):
        #ser.println(str(charge[x]).encode("utf-8"))
        ser.write(str(charge[x]).encode("utf-8"))
        ser.write(str(", ").encode("utf-8"))     
        ser.flush()
        print "EV Charge: ", charge[x], "sent"
        time.sleep(5)
    
send_main()



