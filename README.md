WHAT IS THIS?

- a simple tool for organizing your GoPro stuff

WHAT IS IT NOT?

- a video editor

TELL ME ABOUT FEATURES!

- import your stuff from SD card
- rename files in a more logical order than the GoPro naming convention
- overview about your footage
- create timelapse videos from your stuff via FFmpeg
- localization: English, German

YOU MUST BE JOKING!

- well, these are the basic tasks I usually perform before doing the video editing in kdenlive (use it, it's great)
- I'm thinking about polishing and new features but no warranty that this will get any better

WHAT ABOUT SYSTEM REQUIREMENTS?

- Python 3
- GTK+ 3 (optional, commandline version available)
- FFmpeg (optional)
- GoPro camera

HOW DO I USE IT?

- for commandline version execute ./run-cli.py in a terminal window, you will find out the rest
- for GTK+ version execute ./run-gtk.py

I HAVE SOME IDEAS.
YOUR CODE NEEDS SOME IMPROVEMENTS.
YOU SPELLED XYZ WRONG!

- feel free to contact me or file an issue but be patient I'm a bloody rookie

BUT WAIT - THERE IS MORE!

- there are 2 additional scripts which only help me getting localization done and can be easily ignored. fyi:
        herostuff/localizeorcry.py:     wraps new strings for gettext recognition in the source files and updates translation template and existing po files
        herostuff/po/update_mo.py:      updates all mo files, only needed when translated strings are added to po files
