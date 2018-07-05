#!/usr/bin/env python3

import traceback
import better_exceptions

import threading

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client

import argparse
import random
import time

test_modes  =   ['PLY','MTE','SKP','RVS','RND','DBL','HLF']
loop_modes = ['PLAY','STOP','REVS','RAND']

def send_random_slice():
   new_slice_mode = test_modes[random.randint(0,6)]
   new_loop_i = random.randint(1,4)
   new_slice_i = random.randint(0,7)
   message_string = "/loop/{}/slice/{}".format(new_loop_i,new_slice_i)
   
   client.send_message(message_string,new_slice_mode)
   print("sent: {} {}".format(message_string,new_slice_mode))
   return
   
def send_random_loop():
    new_loop_mode = loop_modes[random.randint(0,3)]
    new_loop_i = random.randint(1,4)
    message_string = "/loop/{}/mode".format(new_loop_i)
    client.send_message(message_string,new_loop_mode)
    print("sent: {} {}".format(message_string,new_loop_mode))
    return

def send_random_volume():
    new_volume = random.randint(0,127)/127.0  # this should now be a float.
    new_loop_i = random.randint(1,4)
    message_string = "/loop/{}/volume".format(new_loop_i)
    client.send_message(message_string,new_volume)
    print("sent: {} {}".format(message_string,new_volume))
    return
    
def set_all_play():
    for i in range(1,5):
        message_string = "/loop/{}/mode".format(i)
        client.send_message(message_string,loop_modes[0])
        for x in range(0,8):
            message_string = "/loop/{}/slice/{}".format(i,x)
            client.send_message(message_string,test_modes[0])
            print("sent: {} {}".format(message_string,test_modes[0]))
            
def set_all_slices_mode(new_mode_index):
    for i in range(1,5):
        for x in range(0,8):
            message_string = "/loop/{}/slice/{}".format(i,x)
            client.send_message(message_string,test_modes[new_mode_index])
            print("sent: {} {}".format(message_string,test_modes[new_mode_index]))

def send_one():
    client.send_message("/loop/1/mode", loop_modes[1])
    client.send_message("/loop/2/mode", loop_modes[1])
    client.send_message("/loop/4/mode", loop_modes[1])
    message_string = "/loop/3/slice/1"
    client.send_message(message_string,test_modes[6])
    print("sent: {} {}".format(message_string,test_modes[6]))

    
if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5080,
      help="The port the OSC server is listening on")
  parser.add_argument("--allplay", action='store_true', help="set all loop and slice playback to PLAY then exits")
  parser.add_argument("--sendone", action='store_true', help="set all loop and slice playback to PLAY then exits")
  parser.add_argument("--setallslicemode",type=int,help="set all slices to the same playback mode", default=-1)
  parser.add_argument("--time",type=float,help="time between random messages",default=0.1)
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)
  #client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  
  if(args.allplay):
      set_all_play()
      exit()
      
  if(args.sendone):
      send_one()
      exit()
  
  if(args.setallslicemode>-1):
      if(args.setallslicemode<7):
          set_all_slices_mode(args.setallslicemode)
          exit()
  
  funfun=[send_random_loop, send_random_slice, send_random_volume]
  
  while True:
      j = random.randint(0,2)
      funfun[j]()
      time.sleep(args.time)
      


#    client.send_message("/loop/2/slice/5", 'RVS')
#    client.send_message("/loop/3/slice/5", 'MTE')
#    client.send_message("/loop/2/slice/2", 'PLY')
    #client.send_message("/","-----------------")
