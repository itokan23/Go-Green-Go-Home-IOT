# -*- coding: utf-8 -*-
"""
Created on Wed Oct 05 12:59:25 2016

@author: dgree
"""

"""
    Simple program structure
    
"""
# listen to serial port and reports stream values to server/database such as pico using Http post requests to web api
# listens to at least 1 data stream by making http get requests every 5 seconds and sends to arduino
import serial
import requests
import json
import time
import datetime
base = 'http://127.0.0.1:5000'
network_id = 'local'
header = {}



print("Start Arduinodatasend (Ctrl+C to stop)")

#change port name to match the port
#to which your arduino is connected
serial_port_name = "COM6" 
ser = serial.Serial(serial_port_name, 9600, timeout=1)

delay = 1*10 # Delay in seconds
x=0
y=0
# Run once at the start
def setup():
    try:
        print "Setup"
    except:
        print "Setup Error"

# Run continuously forever
def loop():
    #check if something is in serial buffer
    if ser.inWaiting() > 0:
        try:
            # Read entire line
            # until '\n'
            # Data is being sent from serial as a strinsg, convert x using float() or int() 
            x = float(ser.readline())
            y = float(ser.readline())
            '''
            while (int(x)>1024):
                x = float(ser.readline())
            while (int(y)!=-1200):
                y = float(ser.readline())    
            '''
            print "Receivedpodlevel:", x
            print "Type:", type (x) 
            print "Received1200:", y
            print "Type:", type (y)
        except:
            print "Error not read"   
    print("sending sinewavedata")
    query = {
        'points-value': x,
        'points-at': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    endpoint = '/networks/local/objects/Arduino/streams/Sinwave/points'
    endpoint2 = '/networks/local/objects/Arduino/streams/Cosine/points'
    response = requests.request('POST', base + endpoint, params=query, headers=header, timeout=120 )
    resp = json.loads( response.text )
    if resp['points-code'] == 200:
        print( 'Update sinewave-stream points: ok')
    else:
        print( 'Update sinwave-stream points: error')
        print( response.text )
    print("sending cosinedata")   
    query = {
        'points-value': y,
        'points-at': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
    response = requests.request('POST', base + endpoint2, params=query, headers=header, timeout=120 )
    resp = json.loads( response.text )
    
    if resp['points-code'] == 200:
        print( 'Update cosine-stream points: ok')
    else:
        print( 'Update cosine-stream points: error')
        print( response.text )    
    time.sleep(0.5)
    
    ############# GETing Processed data ################
    
    
    query = {
        'points-limit': 1
       }   
    
    endpoint = '/networks/'+network_id+'/objects/Arduino/streams/Processed/points'

    response = requests.request('GET', base + endpoint, params=query, headers=header, timeout=120 )
    resp = json.loads( response.text )
    
    if resp['points-code'] == 200 and len(resp['points']) == 1:
        print('Read Processed stream points from server : ok')
        array = json.loads(response.text)
        #print(json.loads(response.text))
        for element in array['points']:
            data = element['value']
            data2=str(data)
        print "Receivedfromserver: ", data
        
    else:
        print('Read Processed stream points from server : error')
         
    ser.write(data2.encode("utf-8"))
    print('data back to Arduino')
    print('data: '), data2.encode("utf-8")
    time.sleep(0.5)
    return

# Run continuously forever
# with a delay between calls
def delayed_loop():
    print "Delayed Loop"

# Run once at the end
def close():
    try:
        print "Close Serial Port"
        ser.close()
    except:
        print "Close Error"
    
# Program Structure    
def main():
    # Call setup function
    setup()
    # Set start time
    nextLoop = time.time()
    while(True):
        # Try loop() and delayed_loop()
        try:
            loop()
            if time.time() > nextLoop:
                # If next loop time has passed...
                nextLoop = time.time() + delay
                delayed_loop()
        except KeyboardInterrupt:
            # If user enters "Ctrl + C", break while loop
            break
        except:
            # Catch all errors
            print "Unexpected error."
    # Call close function
    close()
main()