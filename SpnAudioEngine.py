#!/usr/bin/env python3

import traceback

import better_exceptions

import numpy as np
# import soundfile
# import random
# import time
import sys

from spoon_logging import D, L, W, E

import SpoonModes
MODES = SpoonModes.SpoonSliceModes()

import pyaudio
p = pyaudio.PyAudio()


class SpnAudioEngine():
    """
    Audio engine for Spoon Fight
    This opens the audio interface
    starts the callbacks and mixes the audio loop streams together
    """

    def __init__(self):
        self.BufferSources = []
        self.stream = None
        self.mute = False
        D(" SpnAudioEngine init'd ")
        return

    def set_mute(self, mute_state):
		# set audio to either mute or playing.
		# need to make sure mute_state is a boolean.
        if (mute_state != True or mute_state != False):
            D("ERROR with set_mute: {}".format(str(mute_state)))
            return
        self.mute = mute_state
        D("Audio Mute State: {}".format(str(mute_state)))
        return
		
    def toggle_mute(self):
        # toggles the mute state
        self.mute = (not self.mute)
        L("Mute state toggled.  new state {}".format(str(self.mute)))
        return
		
    def add_source(self, function_name):
        # TODO work out how to make this wokr :p
        """get the function handles for each of the audio loops"""
        self.BufferSources.append(function_name)
        return

    def get_mix(self, num_samples):
        # make a silent array
        ret_data = np.zeros([num_samples, 2])
		
        # get the samples from each of the loops
        for new_func in self.BufferSources:
            # add the audio samples together.  shitty mixing stylez!
            # TODO add better mixing code here.
            # ret_data = ret_data + new_func(num_samples)*0.3
            new_data = new_func(num_samples) * 0.333
            ret_data = ret_data + new_data
        # limit the audio to -1.0 to +1.0
        # https://ristoid.net/research/NL-filters.pdf
        # ret_data = (2.0/((ret_data*ret_data)+1.0)))-1.0
		
		# if Mute is true, return an array of zeros instead.  We don't want to not keep the loops playing though.
        if ( self.mute == True):
            ret_data = np.zeros([num_samples,2])
		
        return ret_data

    def audio_callback(self, in_data, frame_count, time_info, status):
        # do a dummy assign to return silence if we hit an exception below
        # if(frame_count < 0)
        data = np.zeros([frame_count,2])
        try:
            # get data
            data = self.get_mix(frame_count).astype(np.float32).tostring()
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            W("Exception {}".format(str(e)))
            W("frame count: {}  time_info: {} status: {} ".format(frame_count, time_info, status))
            W("Traceback {}".format(repr(traceback.format_tb(exc_traceback))))
            # we got an issue
        return (data, pyaudio.paContinue)

    def stop_audio(self):
        """ Stop the audio callback.  we want to exit cleanly using this"""
        L("Stopping Audio Engine")
        self.stream.stop_stream()
        self.stream.close()
        p.terminate()
        return

    def start_audio(self):
        """Start the audio stream.  setup the callbacks then enter a loop.  """
        L("Starting Audio Engine")
        self.stream = p.open(
            format=pyaudio.paFloat32, channels=2, rate=44100,
            output=True, stream_callback=self.audio_callback)

        self.stream.start_stream()
        return
