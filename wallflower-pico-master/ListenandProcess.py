# -*- coding: utf-8 -*-
"""
Created on Wed Oct 05 16:22:00 2016

@author: dgree
"""

import requests
import json
import time
import serial
import datetime

def setup():
    try:
        print "Setup"
    except:
        print "Setup Error"
def loop():
    base = 'http://127.0.0.1:5000'
    network_id = 'local'
    header = {}
    query = {
        'points-limit': 1
       }   
    endpoint = '/networks/'+network_id+'/objects/Arduino/streams/Sinwave/points'
    response = requests.request('GET', base + endpoint, params=query, headers=header, timeout=120 )
    resp = json.loads( response.text )
    print('Read most recent data stream point : ok:')
    if resp['points-code'] == 200 and len(resp['points']) == 1:
        array = json.loads(response.text)
        #print(json.loads(response.text))
        for element in array['points']:
            data = element['value']
        print "Received: ", data
        data2=float(data)
        processed = 100 * data2 / 2
        base = 'http://127.0.0.1:5000'
        network_id = 'local'
        header = {}
        endpoint = '/networks/'+network_id+'/objects/Arduino/streams/Processed/points'
        query = {
            'points-value': processed,
            'points-at': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }
        response = requests.request('POST', base + endpoint, params=query, headers=header, timeout=120 )
        resp = json.loads( response.text )
     
        if resp['points-code'] == 200:
            print "Upload Processed points: ok:", processed
        else:
            print( 'Upload Processed points: error')
            print( response.text )        
    else:
        print('Read most recent data stream point : error')
        print(response.text)           
    time.sleep(5)
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