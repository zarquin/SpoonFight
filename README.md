# SpoonFight
Spoon Fight is a loop slicer and mangler

To use it, download all the files.

use pip to install the following:
asciimatics
numpy
pyaudio
better_exceptions (not used, but looks nicer when things go wrong)
pythonosc
soundfile

Create a patch file.  copy the testPatch3.patch structure and put your own loop files in there


to start playback:

python SpoonFight.py --patchfile testPatch3.patch

to make things exciting run the test_send.py to send random commands to SpoonFight via OSC.
python test_send.py


