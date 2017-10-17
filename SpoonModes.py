#!/usr/bin/env python3


class SpoonSliceModes(object):
    """ Some Text  """
    PLAY='PLY'
    RANDOM='RND'
    MUTE='MTE'
    SKIP='SKP'
    REVERSE='RVS'
    DOUBLE='DBL'
    HALF='HLF'
    
    
    def __init__(self):
        return
    
    def test_mode():
        return SpoonSliceModes.PLAY
    
    def is_valid_mode(self,mode_to_test):
        valid_slice_modes = [
            SpoonSliceModes.PLAY,
            SpoonSliceModes.RANDOM,
            SpoonSliceModes.MUTE,
            SpoonSliceModes.SKIP,
            SpoonSliceModes.REVERSE,
            SpoonSliceModes.DOUBLE,
            SpoonSliceModes.HALF ]
            
        if mode_to_test in valid_slice_modes:
            return True
        else:
            return False
    
class SpoonLoopModes(object):
    # 6 characters wide
    PLAY='PLAY'  # free play
    STOP='STOP' #not playing
    RANDOM='RAND' #random order of slice playback
    REVERSE='REVS' # reverse order of slice playback
    PLAY_SLAVE='PLY SL' #playback synchronised to a master. if no master, free play
    PLAY_MASTER='PLY MS' # free play, but slaves are synchronized to this.
    
    def is_valid_mode(self,mode_to_test):
        valid_loop_modes = [
            SpoonLoopModes.PLAY,
            SpoonLoopModes.STOP,
            SpoonLoopModes.RANDOM,
            SpoonLoopModes.REVERSE,
            SpoonLoopModes.PLAY_SLAVE,
            SpoonLoopModes.PLAY_MASTER ]

        return mode_to_test in valid_loop_modes
    
class SpoonLoopIDs(object):
    ONE='/loop/1'
    TWO='/loop/2'
    THREE='/loop/3'
    FOUR='/loop/4'
    
class SpoonOSCNames(object):
    LOOP='loop'