# SpoonFight
Spoon Fight is a loop slicer and mangler
"you don't take a spoon to a knife fight"
"I see you've played knifey-spoony before"

To use it: 
1: download all the files.

2: use pip to install the following:
 --asciimatics
 --numpy
 --pyaudio
 --better_exceptions (not used, but looks nicer when things go wrong)
 --pythonosc
 --soundfile

3: Create a patch file.  you can copy the testPatch3.patch structure and put your own loop files in there.
   The existing patch file testPatch3.patch should work with no modifications.

4: to start playback:
  >python SpoonFight.py --patchfile testPatch3.patch

5: to make things exciting run the test_send.py to send random commands to SpoonFight via OSC.
 >python test_send.py

# TODO
These are things that are planned to be done in the immediate future
-standardise on the naming style.  ClassDeclerationsAndFileNamesUseCamelCase.  functions_and_variables_use_this_style
-Add additional OSC handlers for volume, loop playback reset,  an "All Loops" category, etc..
-Create a TouchOSC 'skin' to send loop control messages

In the short term future
-Add Zeroconf support.
-make it handle OSC broadcasts and also send responses to change (primarily so remote control button colours can be set)
-add the handling for config files.  things that might be specified in the config file:
     How are pitch changes (Half and Double) handled?  currently it is done with brute force sample dropping and sample repeating.  this could be changed to be done using various resampling methods.
     what is the sound driver buffer size?

Longer Term
-make the audio for each loop come out of it's own pipe, so it can be processed by a seperate effects application.  Something like JACK would be ideal for this but there doesn't seem to be any current support for python/MacOS
