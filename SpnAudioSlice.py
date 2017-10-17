import better_exceptions
import traceback
import SpoonModes
import numpy as np
import random

MODES = SpoonModes.SpoonSliceModes()

from spoon_logging import D, L, W, E

# the slice holds the audio data.
# the slice is asked to return the audio data.
# any order/skip/frequency changes are done in the playback section of slice


class SpnAudioSlice():

    play_mode = MODES.PLAY
    slice_length = 0
    # pointer to where we are in the slice
    slice_pointer = 0
    # this is the number of samples left in this playback.  this is important to maintain for reandom playback
    slice_remaining = 0
    # do i need playback counter ??
    playback_counter = 0

    def __init__(self, new_wave_slice_data):
        self.slice_wave_data = new_wave_slice_data
        self.slice_length = len(new_wave_slice_data)
        self.play_mode = MODES.PLAY
        self.slice_pointer = 0
        self.slice_remaining = self.slice_length
        # add logging here
        return

    def drop_samples(self, old_array):
        # drop half the samples in the array so we can double playback speed
        # set the new length of the array.
        #new_length = int(len(old_array) / 2)
        #new_array = np.empty([new_length, 2])
        # copy samples
        #for i in range(0, new_length):
        #    new_array[i] = old_array[i * 2]
        new_array = old_array[::2]
        D("drop samples using view len-new:{} len-old:{}".format(len(new_array),len(old_array)))

        return new_array
                
    def repeat_samples(self, old_array):
        # newLen = 2*len(old_array)
        #new_array = np.empty([0, 2])
        #for i in old_array:
        #    new_array = np.vstack((new_array, i))
        #    new_array = np.vstack((new_array, i))
        #D("repeated samples old:{}  new:{}".format(len(old_array),len(new_array)))
        new_array = np.repeat(old_array,2,axis=0)
        D("np.repeat len-new:{} len-old:{}".format(len(new_array),len(old_array)))
        return new_array
    
    def repeat_last_sample(self, old_array):
        if len(old_array)<1:
            D("old_array length was too short! {}".format(old_array))
            return old_array
        last_sample = old_array[len(old_array) - 1]
        return np.vstack((old_array, last_sample))
        
    def set_play_mode(self, new_play_mode):
        """sets the playback mode """
        self.play_mode = new_play_mode
        # if mode is REVERSE we need to set the slice_pointer to a new location
        if(self.play_mode == MODES.REVERSE):
            self.slice_pointer = self.slice_remaining - 1
        else:
            self.slice_pointer = self.slice_length - self.slice_remaining   
        # do a test for sillyness
        if((self.slice_pointer > self.slice_length) or
           (self.slice_pointer < 1) or
           (self.slice_remaining < 1)):
            self.reset_playback()
        return

    def reset_playback(self):
        """resets slice playback counters."""
        self.slice_pointer = 0
        self.slice_remaining = self.slice_length
        self.playback_counter = 0
        if(self.play_mode == MODES.REVERSE):
            self.slice_pointer = self.slice_length - 1
        return
        
    # slice playback function
    def get_samples(self, number_of_samples):
        """
        returns BOOL, numpy_array
        return a numpy array of the number of samples requested.
        if there are not enough samples left return a shorter length array.
        If all the samples are returned then BOOL is true, otherwise it is false.
        This will inform the slice-sequencer that the next slice in the sequence needs to be played.
        """
        # all ok, not going to hit the end of the samples
        temp_samples_to_play = number_of_samples
        temp_returned_all_samples = True
        if((number_of_samples > self.slice_remaining) and (self.play_mode != MODES.HALF)):
            # TODO is this incorrect  when reading at HALF speed?
            # uh oh, not all ok, we need to work with a smaller number of samples
            # TODO add logging here
            # logging.debug(str.format("hit end of slice:{} ", self.slice_remaining))
            
            temp_samples_to_play = self.slice_remaining
            temp_returned_all_samples = False
    
        if(self.play_mode == MODES.HALF):
            # half is half speed. so we read half the number of samples from the array and then double each sample.
            # calculate the number of actual samples we're going to pull from teh array
            D("HALF samples req: {} , temp_samples to play back: {}".format(number_of_samples, temp_samples_to_play))
            temp_samples_to_play = int(number_of_samples / 2)
            D("HALF samples req: {} , temp_samples to read from slice: {} rem in slice:{}".format(number_of_samples, temp_samples_to_play, self.slice_remaining))
            if(temp_samples_to_play > self.slice_remaining):
                # if we still have no enought samples left, need to set flags and update values
                temp_samples_to_play = self.slice_remaining
                temp_returned_all_samples = False
        
        if(self.play_mode == MODES.DOUBLE):
            # double speed playback.  drop samples.
            temp_samples_to_play = int(number_of_samples * 2)
            D("D samples req: {} , temp_samples to play back: {} rem in slice:{}".format(number_of_samples, temp_samples_to_play, self.slice_remaining))
            if(temp_samples_to_play > self.slice_remaining):
                temp_samples_to_play = self.slice_remaining
                temp_returned_all_samples = False
        
        # create an empty numpy array for stereo data.
        slice_ret_data = np.zeros([0, 2])
        
        if(number_of_samples == 0):
            # if the number of samples requested is none/zero, return empty
            return False, slice_ret_data
        
        if(self.play_mode == MODES.SKIP):
            # if the mode is skip, 
            # return an empty slice and also a False so the sequencer knows to get data from the next sample
            return False, slice_ret_data
        
        if(self.play_mode == MODES.RANDOM):
            # if the slice playback is random, then select a random offset in the sample, 
            # and playback number_of_samples
            # slice_remaining count must remain accurate.
            # get a sample pointer somewhere in the slice
            self.slice_pointer = random.randint(0, self.slice_length - temp_samples_to_play)
            
        if(self.play_mode == MODES.PLAY or self.play_mode == MODES.RANDOM or self.play_mode == MODES.HALF or self.play_mode == MODES.DOUBLE):
            # forward playback mode
            slice_ret_data = self.slice_wave_data[self.slice_pointer:(self.slice_pointer + temp_samples_to_play)]
            # if( self.play_mode == HALF):
            #    dprint("{} ~ {}".format(len(slice_ret_data),temp_samples_to_play))
          
        if(self.play_mode == MODES.MUTE):
            # if we're muting the playback, we just want to set all teh wave data to 0
            # but playback length is the same etc.
            slice_ret_data = np.zeros([temp_samples_to_play, 2])
        
        if(self.play_mode == MODES.REVERSE):
            slice_ret_data = np.flipud(self.slice_wave_data[(self.slice_pointer - temp_samples_to_play):self.slice_pointer])

        if(self.play_mode == MODES.HALF):
            # dprint("HALF: old length {}".format(len(slice_ret_data)))
            slice_ret_data = self.repeat_samples(slice_ret_data)
            # dprint("HALF: new length {}".format(len(slice_ret_data)))
            # need to make sure that if we've been asked for an ODD number of samples we're handling it ok
            if(temp_returned_all_samples and (len(slice_ret_data) != number_of_samples)):
                # we haven't run out of samples, but length doesn't match. it should only be off by 1 for a divide by 2
                # repeat the last sample as a shitty way to pad it out
                D("HALF: unbalanced. need to add aditional sample: ret {} req {}".format(len(slice_ret_data), number_of_samples))
                while(len(slice_ret_data) < number_of_samples):
                    slice_ret_data = self.repeat_last_sample(slice_ret_data)
        
        if(self.play_mode == MODES.DOUBLE):
            # we're already read twice the samples needed.  just need to drop half the samples   
            slice_ret_data = self.drop_samples(slice_ret_data)
            # add a safety check. this should never get called since we're grabbing twice as many samples as we're asked for.
            # so it should always be an even number.
            if(temp_returned_all_samples and (len(slice_ret_data) != number_of_samples)):
                # we haven't run out of samples, but length doesn't match. it should only be off by 1 
                # repeat the last sample as a shitty way to pad it out
                D("DOUBLE: ret {} req {}".format(len(slice_ret_data), number_of_samples))
                if(len(slice_ret_data) < number_of_samples):
                    slice_ret_data = self.repeat_last_sample(slice_ret_data)
                if(len(slice_ret_data) > number_of_samples):
                    # if it's too long, trim off then end sample
                    slice_ret_data = slice_ret_data[0:(number_of_samples - 1)]
            
        # cleanup time
        # update slice_remaining and slice_pointer
        self.slice_remaining = self.slice_remaining - temp_samples_to_play  # number_of_samples
        if(self.play_mode != MODES.REVERSE):
            self.slice_pointer = self.slice_pointer + temp_samples_to_play  # number_of_samples
        else:
            self.slice_pointer = self.slice_pointer - temp_samples_to_play  # number_of_samples
        # check for reset conditions.
        if((temp_returned_all_samples is False) or (self.slice_remaining < 1) 
        or (self.slice_pointer < 0) or (self.slice_pointer > self.slice_length)):
            # TODO add loging here
            D("slice as run out of samples, and we're resetting the playback counters")
            self.reset_playback()
                                                         
        return temp_returned_all_samples, slice_ret_data

