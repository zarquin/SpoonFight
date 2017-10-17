#!/usr/bin/env python3

import traceback
import better_exceptions

import threading
import SpoonModes
import numpy as np
import random

MODES = SpoonModes.SpoonSliceModes()
LM = SpoonModes.SpoonLoopModes()

from spoon_logging import D, L, W, E

from pythonosc import dispatcher
from pythonosc import osc_server


def set_slice_mode(loop_number, slice_number, new_mode, the_status_obj):
    loop_id_s = "/loop/{}".format(loop_number)
    the_status_obj.loops[loop_id_s].set_slice_mode(slice_number,new_mode)
    D("set the slice mode {} : {} : {} ".format(loop_id_s, slice_number, new_mode))
    
def set_loop_mode(loop_number, new_mode, the_status_obj):
    loop_id_s = "/loop/{}".format(loop_number)
    the_status_obj.loops[loop_id_s].set_loop_mode(new_mode)
    D("set the loop mode {} : {} ".format(loop_id_s, new_mode))

def loop_mode_callback(unused_addr, args, the_OSC_message_argument):
    D("LoopCallback")
    #print("{} {} {} ".format(unused_addr, args, the_obj))
    message_ok = True
    
    if(len(unused_addr) != 12):
        message_ok = False
    loop_i = -1
    new_mode = 'NOT-SET'
    
    the_status_obj = args[0]
    try:
        loop_s = unused_addr[6]
        loop_i = int(loop_s)
        
    except Exception as jeje:
        L("exception in handling OSC message {}".format(unused_addr))
        L("Exception: {}".format(jeje))
        L("{}".format(repr(jeje)))
        message_ok = False
    
    if(loop_i >4 or loop_i < 1):
        D("Loop value out of range {} ".format(loop_i))
        #do nothing
        message_ok = False
        
    new_slice_mode = the_OSC_message_argument
    if not LM.is_valid_mode(new_slice_mode):
        message_ok = False
        
    if(message_ok):
        set_loop_mode(loop_i, new_slice_mode, the_status_obj)
        the_status_obj.set_osc_message( "{} : {}  DONE".format(unused_addr, the_OSC_message_argument))
    else:
        # log error message
        #TODO fix this error message
        L("unable to parse message {} {} ".format(unused_addr, the_OSC_message_argument))
        the_status_obj.set_osc_message( "{} : {}  FAIL".format(unused_addr, the_OSC_message_argument))
        return
    #print("Loop:{}  slice:{}".format(loop_i,slice_i))  
    return
    
    
def slice_callback(unused_addr, args, the_OSC_message_argument):
    D("SliceCallback")
    #print("{} {} {} ".format(unused_addr, args, the_obj))
    message_ok = True
    
    if(len(unused_addr) != 15):
        message_ok = False
    loop_i = -1
    slice_i = -1
    new_mode = 'NOT-SET'
    
    the_status_obj = args[0]
    #probably should do a type() check here on the_status_obj
  
    try:
        loop_s = unused_addr[6]
        slice_s = unused_addr[14]
        loop_i = int(loop_s)
        slice_i = int(slice_s)
        
    except Exception as jeje:
        L("exception in handling OSC message {}".format(unused_addr))
        L("Exception: {}".format(jeje))
        L("{}".format(repr(jeje)))
        message_ok = False
        
    if(loop_i >4 or loop_i < 1):
        D("Loop value out of range {} ".format(loop_i))
        #do nothing
        message_ok = False
        
    if(slice_i<0 or slice_i>7):
        D("slice value out of range {} ".format(slice_i))
        #do nothing
        message_ok = False
    
    #check is the_OSC_message_argument is a correct slice mode
    
    new_slice_mode = the_OSC_message_argument
    if not MODES.is_valid_mode(new_slice_mode):
        message_ok = False
        
    if(message_ok):
        set_slice_mode(loop_i,slice_i, new_slice_mode, the_status_obj)
        the_status_obj.set_osc_message( "{} : {}  DONE".format(unused_addr, the_OSC_message_argument))
    else:
        # log error message
        #TODO fix this error message
        L("unable to parse message {} {} ".format(unused_addr, the_OSC_message_argument))
        the_status_obj.set_osc_message( "{} : {}  FAIL".format(unused_addr, the_OSC_message_argument))
        return
    #print("Loop:{}  slice:{}".format(loop_i,slice_i))  
    return

def default_callback(unused_addr, args):
    L("unknown message {} {}".format(unused_addr, args))
    return

def start_OSC_server(spoon_status_object):
    
    disp = dispatcher.Dispatcher()

    disp.map("/loop/*/slice/*", slice_callback, spoon_status_object)
    disp.map("/loop/*/mode", loop_mode_callback, spoon_status_object)
    disp.set_default_handler(default_callback)
    
    new_osc_port = spoon_status_object.osc_port
    
    server = osc_server.ThreadingOSCUDPServer( ("127.0.0.1", new_osc_port), disp)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    L("Serving on {}".format(server.server_address))
    #return the server and thread so we can shut it down when we quit
    # server.shutdown()
    return server , server_thread
