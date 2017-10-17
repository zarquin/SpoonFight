#SpnPatchParser.py
"""
This is a patch file parser for spoon fight.
A patch really is just a collection of audio files and slices if specified

[loop_name]
filepath:pathtofile
slicepoints: 0 , 123, 231, 300,   #if slicepoints are listed, then this has priority as long as it's real.
#or
slicestyle: even #or peak

"""

from spoon_logging import D, L, W, E
import soundfile
import configparser

class SpnLoopFile:
    #this is a path to an audio file, and slice points.
    loop_filename = None #
    slice_points=[]  #
    sample_rate=0
    
    #these values have already been tested for correctness 
    def __init__(self, filename, sample_rate, slice_points, section_name ):
        self.loop_filename = filename
        self.sample_rate = sample_rate
        self.slice_points=slice_points
        self.audio_section_name = section_name
        return
    
    def set_slice_points(self, new_slice_points):
        self.slice_points = new_slice_points
        return
        
    def get_audio_data(self):
        #returns the audio array object of the loop
        data , samplerate = soundfile.read(self.loop_filename)
        return data
        
    def get_slice_points(self):
        #returns the array of slice tuples.
        return self.slice_points
    
    def to_string(self):
        return "file:{} smprte:{} slicepoints:{}".format(self.loop_filename, self.sample_rate, self.slice_points)
     


def test_file_correctness(audio_file_path):
    #TODO make this actually test the file
    #returns true if the file is OK.  false otherwise
    # D("trying to open: {}".format(audio_file_path))
    try:
        j = soundfile.info(audio_file_path)
        # D("{} :  soundfile info {}".format(audio_file_path, str(j)))
        
        #TODO add more supported formats in a future time
        if(j.samplerate ==44100 and j.channels==2 ):
            L("File {} is OK.".format(audio_file_path))
            return True
        else:
            W("File {} is NOT OK. Sample rate is {} and channels are {}".format(audio_file_path, j.samplerate, j.channels))
            return False
    except Exception as e:
        W("Error opening file {}. Message was {}".format(audio_file_path, repr(e) ))
    #if we have got to this point, we've failed the try/except so there is a filepath or permissions problem. return False
    return False

def get_simple_slice_points(file_path):
    #super easy and simple function that gives back evenly spaced tuples of slice points
    j = soundfile.read(file_path)[0]
    """returns an array of tuples
        these are the 8 slice pairs
    """
    #TODO make this a seperate class that can use different slice techniques
    slice_length = int(len(j)/8  )
    points = []
    for i in range(8):
        x_x= i*slice_length, (i+1)*slice_length
        points.append(x_x)
    #set the end of the last one to be the length of the audio sample to remove any rounding errors    
    points[7] = points[6][1], len(j)
    return points

    
def make_loop_from_section(config_name, config_section):
    #takes a config section and creates and returns a loop object
    #if there are loop points defined, add them. 
    temp_file_path = config_section['filepath']
    temp_slice_points = get_simple_slice_points(temp_file_path)
    temp_sample_rate = 44100
    new_loop_file_object = SpnLoopFile(temp_file_path, temp_sample_rate, temp_slice_points, config_name)
    # D("{} created new SpnLoopFile {}".format( config_name, new_loop_file_object.get_string() ) )
    return new_loop_file_object
        

def SpnPatchParser(patch_file_name):
    #opens a config file and gets the loop file names and any details in them
    looper_files = [] #an array of the section names.
    config = configparser.ConfigParser()
    config.read(patch_file_name)
    D("loaded config file {}".format(patch_file_name))
    # D("sections loaded: {}".format(config.sections() ))
    for xerw in config.sections():
        #loop through the sections
        #if the filepath is set make a SpnLoopFile Object 
        if 'filepath' in config[xerw]:
            temp_path = config[xerw]['filepath']
            if test_file_correctness(temp_path):
                looper_files.append( make_loop_from_section(xerw,config[xerw]))
            else:
                W("Error in: {} ;audio file: {}".format(repr(xerw),repr(config[xerw])))
    
    D("done adding sections")
    return looper_files
