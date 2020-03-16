import sys
import zmq
from multiprocessing import Process, Array , Manager
sys.path.append('../')
from utility import log 
import random

def tracker(id , no_keepers , ips , port ,  status_table , lookup_table , free_ports):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    counter = 0
    while True:
    #  Wait for next request from client
        message = socket.recv_pyobj()
        lis = []
        lis2 = []
        count = 0
        log("Keeper " + str(id) +": Client request " + message["type"] +" filename " + message["file"] ) 
        if(message["type"] == "upload"):
            if( message["file"] in lookup_table.keys() ):
                socket.send_pyobj({"error": "Filename already exists"})
                log("Keeper" + str(id) + ": Filename already exists" )
            else :    
                while count < 1 :       # Only one data keeper needed
                    try:
                        while(not status_table[counter]):
                            counter = (counter + 1)% no_keepers
                        temp = free_ports[counter]
                        x = str(temp.pop(0))
                        free_ports[counter] = temp
                        lis.append(x)
                        lis2.append(str(ips[counter]))
                        count += 1
                        counter = (counter + 1)% no_keepers
                    except:
                        pass
                socket.send_pyobj({"ports" : lis , "ips" : lis2})
                log("Keeper" + str(id) + ": Respond to upload request" )
        elif( message["type" ] == "download"):
            filename = message["file"]
            nodes = lookup_table[filename]
            y = random.choice(nodes)
            while(not status_table[int(y)]):
                y = random.choice(nodes)
            while count < 1 :       # Get only 1 ip and 1 port
                try:
                    temp = free_ports[int(y)]
                    x = temp.pop(0)
                    free_ports[int(y)] = temp
                    lis.append(str(x))
                    lis2.append(ips[int(y)])
                    count += 1
                except:
                    y = random.choice(nodes)
            socket.send_pyobj({"ports" : lis, "ips" : lis2})
            log("Tracker id: " + str(id) + " ,Respond to upload request : " + lis[0] + ":" + lis2[0] )