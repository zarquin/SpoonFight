#!/usr/bin/env python3

import traceback
import better_exceptions
import numpy as np
import soundfile
import random
import time
import sys
import argparse

import SpoonModes
import SpnPatchParser

from asciimatics.screen import Screen

from spoon_logging import D, L, W, E
from SpnAudioEngine import SpnAudioEngine
from SpnAudioLoop import SpnAudioLoop
from SpnPatchParser import SpnLoopFile
from SpnTUI import draw_the_tui
from SpnOSCReceiver import start_OSC_server

MODES= SpoonModes.SpoonSliceModes()
LOOP_MODES= SpoonModes.SpoonLoopModes()

DESC_LONG="""
SpoonFight.py
I see you've played Knifey-Spooney before!
This is a 4 track loop player.
controlled by OSC
"""

VERSION_INFO="""

"""

DESC_NAME = """
░█▀▀░█▀█░█▀█░█▀█░█▀█░░░█▀▀░▀█▀░█▀▀░█░█░▀█▀
░▀▀█░█▀▀░█░█░█░█░█░█░░░█▀▀░░█░░█░█░█▀█░░█░
░▀▀▀░▀░░░▀▀▀░▀▀▀░▀░▀░░░▀░░░▀▀▀░▀▀▀░▀░▀░░▀░

 """
 
class SpoonFightStatus:
    # this class holds the status of the spoon fight
    """
    Attributes:
        status_message.  this is the message that goes accross the top in the banner.
        loops
        osc_port
        osc_message  this is the latest action that has been sent via OSC
        event_history  this is a history of osc and status messages
    """
    
    def __init__(self, new_osc_port):            
        self.status_message = "starting"    
        #dictionary to store the loops
        self.loops = {'/loop/1': None, '/loop/2': None, '/loop/3': None, '/loop/4': None }
        
        #event history
        self.event_history = [] #empty list
        self.osc_port = new_osc_port
        self.osc_message = "OSC starting"
        self.verbose_flag = False
        self.audio_loop_files = [] #empty list.  populate from patch file.
        return

    def set_status_message(self, new_message, verbose_message=False):
        #if it's a message to display in verbose mode, verbose_message will be true and verbose_flag will be true
        if(verbose_message and not self.verbose_flag ):
            # requesting a verbose print and verbose flag is not set return doing nothing
            return
        
        self.status_message = new_message
        self.event_history.append('S: {}'.format(new_message) )
        return
    
    def add_audio_loop_files(self, loops_to_add):
        self.audio_loop_files.append(loops_to_add)
        return
    
    def load_new_audio_file_by_index(self, loop_name, file_index):
        # try to load a new file into a loop.
        # is the requested file index available?
        
        if(file_index <0 or file_index >= len(self.audio_loop_files) ):
            # file index is out of bounds.  give feedback and return without doing anything else.
            self.set_status_message(" Attempted to set new loop{} file. out of bounds {}".format(loop_name, file_index))
            self.set_status_message(" there are {} audio files avalaible".format(len(self.audio_loop_files)))
            return
        # numbers make sense. let's change over the audio buffers.
        # get the audio file and slice point information and copy over.
        temp_audio_data = self.audio_loop_files[file_index].get_audio_data()
        temp_slice_points = self.audio_loop_files[file_index].get_slice_points()
        temp_name = self.audio_loop_files[file_index].audio_section_name
        
        #stop the loop.
        self.loops[loop_name].set_loop_mode(LOOP_MODES.STOP)
        
        # clear the existing audio slices.
        self.loops[loop_name].dump_audio_slices()
        #copy data over.
        self.loops[loop_name].set_audio_buffer( temp_audio_data, temp_slice_points )
        self.loops[loop_name].set_audio_file_name(temp_name )
        # let user know audio loop has been changed over.
        self.set_status_message("New Audio File loaded for {}".format(loop_name))
        
        return
    
    
    def set_osc_message(self, new_message, verbose_message=False):
        #if it's a message to display in verbose mode,  verbose_message will be true and verbose_flag will be true
        if(verbose_message and not self.verbose_flag ):
            # requesting a verbose print and verbose flag is not set return doing nothing
            return
        self.osc_message = new_message
        self.event_history.append('OSC: {}'.format(new_message) )
        return


# this function is now inside SpnPatchParser
def get_loop_points(audio_file):
    """returns an array of tuples
        these are the 8 slice pairs
    """
    #TODO make this a seperate class that can use different slice techniques
    slice_length = int(len(audio_file)/8  )
    points = []
    for i in range(8):
        x_x= i*slice_length, (i+1)*slice_length
        points.append(x_x)
    #set the end of the last one to be the length of the audio sample to remove any rounding errors    
    points[7] = points[6][1], len(audio_file)
    return points
    

def loop_till_forever(screen):
    global spoon_fight_status
    global audioEngine
    running=True
    while(running):
        
        #SpnTUI.draw_the_tui(screen, spoon_fight_status)
        draw_the_tui(screen, spoon_fight_status)
        
        ev = screen.get_key()
        if ev in (ord('Q'), ord('q')):
            running=False

        if ev in (ord('M'), ord('m')):
            #mute or un-mute audio
            am_i_muted=audioEngine.toggle_mute()
            spoon_fight_status.set_status_message("Mute toggled. currently {}".format(am_i_muted))
		
        screen.refresh()
        time.sleep(0.05)
    
    #time.sleep(10)
    
    #if we quit clean up audio
    audioEngine.stop_audio()
    return

def main():
      
    parser = argparse.ArgumentParser(
    description=DESC_NAME , formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--oscport',help='Port OSC listens on', action="store", type=int, default=5080)
    parser.add_argument('--patchfile', help='Patch file to load', action="store", required=True)
    parser.add_argument('--tuirefresh',help='refresh rate for UI.  This is for slow networked shell connections', action="store", default=20)
    parser.add_argument('--configfile',help='config file to load NOT IMPLEMENTED', action="store")
    parser.add_argument('--verbose', help= 'Turn on verbose mode', action='store_true', default=False )
    parser.add_argument('--version', help='Display version information', action='version', version='%(prog)s 0.0')
    
    args = parser.parse_args()
    
    #create the audio engine
    global audioEngine
    audioEngine = SpnAudioEngine()
    
    #create the status 
    global spoon_fight_status
    spoon_fight_status = SpoonFightStatus( args.oscport)
     
    #create the four loops
    spoon_fight_status.loops['/loop/1'] = SpnAudioLoop('/loop/1')
    spoon_fight_status.loops['/loop/2'] = SpnAudioLoop('/loop/2')
    spoon_fight_status.loops['/loop/3'] = SpnAudioLoop('/loop/3')
    spoon_fight_status.loops['/loop/4'] = SpnAudioLoop('/loop/4')
    
    # add the loop audio to the audioengine
    for i in spoon_fight_status.loops:
        audioEngine.add_source( spoon_fight_status.loops[i].get_audio )
    
    # open patch file
    ret_loops = SpnPatchParser.SpnPatchParser(args.patchfile)
    
    spoon_fight_status.set_status_message("loaded {} loops".format(len(ret_loops)))
    
    for at in ret_loops:
        spoon_fight_status.add_audio_loop_files(at)
    
    i=0
    spoon_fight_status.loops['/loop/1'].set_audio_buffer( ret_loops[i].get_audio_data(),ret_loops[i].get_slice_points() )
    spoon_fight_status.loops['/loop/1'].set_audio_file_name(ret_loops[i].audio_section_name )
    
    spoon_fight_status.loops['/loop/1'].loop_mode = LOOP_MODES.STOP
    i=1
    spoon_fight_status.loops['/loop/2'].set_audio_buffer( ret_loops[i].get_audio_data(),ret_loops[i].get_slice_points() )
    spoon_fight_status.loops['/loop/2'].set_audio_file_name(ret_loops[i].audio_section_name )
    spoon_fight_status.loops['/loop/2'].loop_mode = LOOP_MODES.STOP
    i=2
    spoon_fight_status.loops['/loop/3'].set_audio_buffer( ret_loops[i].get_audio_data(),ret_loops[i].get_slice_points() )
    spoon_fight_status.loops['/loop/3'].set_audio_file_name(ret_loops[i].audio_section_name )
    spoon_fight_status.loops['/loop/3'].loop_mode = LOOP_MODES.STOP
    i=3
    spoon_fight_status.loops['/loop/4'].set_audio_buffer( ret_loops[i].get_audio_data(),ret_loops[i].get_slice_points() )
    spoon_fight_status.loops['/loop/4'].set_audio_file_name(ret_loops[i].audio_section_name )
    spoon_fight_status.loops['/loop/4'].loop_mode = LOOP_MODES.STOP
    
    # start the OSC server
    # returns a tuple of OSC server, and the thread it is in.
    local_server, local_server_thread = start_OSC_server(spoon_fight_status)
    spoon_fight_status.set_status_message("started OSC server")
                
    audioEngine.start_audio()
    spoon_fight_status.set_status_message("started audio engine")
    
    #TODO put the main loop in here.
    
    Screen.wrapper(loop_till_forever)
    
    D("shuting down threads")
    local_server.shutdown()
    D("OSC Server thread stopped")
    audioEngine.stop_audio()
    D("Audio Thread stopped")
    
    return



if __name__ == "__main__":
    main() 
 