#!/usr/bin/env python3
import traceback
import better_exceptions

import numpy as np
import soundfile
import random
import time
import sys

from SpnAudioSlice import SpnAudioSlice

import SpoonModes

MODES=SpoonModes.SpoonSliceModes()
LOOP_MODES=SpoonModes.SpoonLoopModes()

from spoon_logging import D, L, W, E

class SpnAudioLoop():
       
    def __init__(self, new_name):
        self.audio_buffer_set = False
        self.audio_buffer = None
        self.slice_points = None
        self.audio_slices = []
        self.current_slice =0
        self.all_slices_muted = False
        self.loop_mode = LOOP_MODES.PLAY
        self.name = new_name
        self.audio_file_name = "unset"
        self.volume_gain = 1.0
        return
    
    def set_audio_file_name(self, new_audio_name):
        self.audio_file_name = new_audio_name
        return
     
    def dump_audio_slices(self):
        # this resets the array containing the audio buffers so we can load a new audio file.  
        # this will cause the slices to loose their state when a new loop is loaded with set_audio_buffer
        # this would require refactoring set_audio_buffer and how audio is loaded into the loop and slices.
        self.audio_slices = []
        D("audio slices dumped for {}".format(self.name))
        return
     
    def set_audio_buffer(self,new_audio_buffer, new_slice_points):
        #divide the audio up into slice objects
        self.audio_buffer = new_audio_buffer
        self.slice_points = new_slice_points #slice points are tuples 0 for start, 1 for ending point
        
        first = 0
        for j in new_slice_points:
            x=SpnAudioSlice( new_audio_buffer[ j[0]: j[1]  ] )
            x.set_play_mode(MODES.PLAY)
            D("made new slice {} {} ".format( repr(x), j,  ))
            self.audio_slices.append(x)
        D("Completed adding slices")
        return
    
    def detect_all_skip(self):
        """detect if all slices are silenced and returns true if all slices are in skip mode"""
        allSkipMode = 0       
        for s in self.audio_slices:
            if (s.play_mode == MODES.SKIP):
                allSkipMode +=1
        if (allSkipMode > 7):
            D("all slices in skip mode")
            return True
        else:
            return False
    
    def set_all_slice_modes_random(self):
        for i in self.audio_slices:
            #TODO fix this.
            i.set_play_mode( MODES.PLAY)     
        return
    
    def set_all_slice_modes(self, newmode):
        #don't allow allmodes to be skip
        if newmode ==MODES.SKIP:
            return            
        for i in self.audio_slices:
            i.set_play_mode(newmode)
        return
    
    def reset_looping(self):
        self.current_slice = 0
        for j in self.audio_slices:
            j.reset_playback()
        return
    
    def jump_slice(self, new_position):
        i = self.current_slice
        #set the new slice position.
        self.current_slice = new_position
        #reset the previous slice audio 
        self.audio_slices[i].reset_playback()
        return
    
    def set_volume(self, new_volume):
        # if the volume value is a float then we can set it
        if(type(new_volume)==type(1.0)):
            self.volume_gain = new_volume
        else:
            D(" Set Volume failed. {} {}".format(type(new_volume),new_volume))
            return
        #limit volume to 0.0 - 1.0
        
        if (self.volume_gain > 1.0):
            self.volume_gain =1.0
        
        if (self.volume_gain<0.0):
            self.volume_gain = 0.0
        
        D(" Set Volume {} {}".format(type(new_volume),new_volume))
        return
    
    def set_loop_mode(self, new_mode):
        self.loop_mode = new_mode
        return
    
    def set_slice_mode(self, slice_num,new_mode):
        self.audio_slices[slice_num].play_mode = new_mode
        return
        
    def get_slice_modes(self):
        slice_modes=[]       
        for i in self.audio_slices:
            slice_modes.append(i.play_mode)
        return slice_modes
        
    def update_next_slice_reverse(self):
        self.current_slice-=1
        if(self.current_slice<0):
            self.current_slice=7
            D(" current slice wrapped around in reverse mode")
        return
    
    def update_next_slice_forward(self):
        self.current_slice+=1
        if(self.current_slice >7):
            self.current_slice =0
            D(" current slice wrapped around in forward mode")
        return
    
    def update_next_slice_random(self):
        self.current_slice = random.randint(0,7)
        return
     
    def update_next_slice(self):
        """sets the self.current_slice to the next value"""
        #TODO updated this so we can have different audio slice pattersn.  reverse, random etc.
        old_slice = self.current_slice
        nek_slice = {
             LOOP_MODES.PLAY: self.update_next_slice_forward,
             LOOP_MODES.REVERSE: self.update_next_slice_reverse,
             LOOP_MODES.RANDOM: self.update_next_slice_random
        }
        if self.loop_mode in nek_slice.keys():
             nek_slice[self.loop_mode]()
        else:
            update_next_slice_forward()        
        D("{} Updated slice was {} now {} mode {}".format(self.name, old_slice, self.current_slice, self.loop_mode))
        return
       
    def get_audio(self, number_of_samples):
        #return audio 
        ret_data = np.zeros([0,2])
        temp_remaining = number_of_samples
        
        #if the slices don't exist or are being loaded, return silence.
        if(len(self.audio_slices)<8):
            D(" slices empty, returning silence")
            ret_data = np.zeros([number_of_samples,2])
            return ret_data
        
        #if all the slices are muted, return silence.
        if(self.all_slices_muted or self.loop_mode == LOOP_MODES.STOP or self.detect_all_skip() ):
            ret_data = np.zeros([number_of_samples,2])
            return ret_data
        
        # work out which slice to get from
        # while there is still audio to be put in the buffer, get audio from the slice.
        while(temp_remaining >0):
            temp_state, temp_data = self.audio_slices[self.current_slice].get_samples(temp_remaining)
            D( str.format("{} temp_stat:{} temp_data:{} temp_rem:{}", self.name, str(temp_state), len(temp_data),temp_remaining))    
            ret_data = np.concatenate((ret_data,temp_data))
            temp_remaining = temp_remaining -len(temp_data)
            
            #detect all skip mode during the middle of buffer playback
            if(self.detect_all_skip()):
                temp_data = np.zeros([temp_remaining,2])
                ret_data = np.concatenate((ret_data,temp_data))
                # this should set temp_remaining to zero
                temp_remaining = temp_remaining - len(temp_data)
            
            # if returned audio is less than the amount requested, and temp_stat is not set properly, need to note this.
            if(temp_remaining > 0 and temp_state):
                #should reset the current slice and then move on.
                # hand of god style
                D("ALERT: returned samples was less than requested, and temp_state was still true. ")
                D("Slice {}, Slicemode {}, temp_remaining:{} len(temp_data):{}  ".format(
                    self.current_slice, self.audio_slices[self.current_slice].play_mode, 
                    temp_remaining, len(temp_data)))
                # reset playback to clean up
                self.audio_slices[self.current_slice].reset_playback()
                # set to false to force slice update
                temp_state=False
                
            if(temp_state==False):  #temp_state is false when the  slice has run out of samples
               self.update_next_slice()
            
        ret_data = ret_data *self.volume_gain
                 
        D(str.format("{} slice:{} temp remaining:{} sample length {}",self.name, self.current_slice,temp_remaining, len(ret_data)))                           
        return ret_data

  
    
            