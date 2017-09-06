WHAT IS THIS?

- a simple tool for organizing your GoPro stuff

WHAT IS IT NOT?

- a video editor
- professional

TELL ME ABOUT FEATURES!

- import your stuff from SD card
- rename files in a more logical order than according to the GoPro naming convention
- overview of your footage, directly rename folders
- create timelapse videos from your stuff via FFmpeg
- localization: English, German
- open older content as Kdenlive project
- (experimental) extended application window with fancy video preview and media information

YOU MUST BE JOKING!

- well, these are the basic tasks I usually perform before doing the video editing in Kdenlive (use it, it's great)
- I'm thinking about polishing and new features but no warranty that this will get any better

WHAT ABOUT SYSTEM REQUIREMENTS?

- Python 3
- Python 3 bindings for GObject (Gtk+ 3 (optional, commandline version available))
- FFmpeg (optional)
- GStreamer and MediaInfo for the extended application window
- GoPro camera

HOW DO I USE IT?

- for commandline version execute `./run-cli.py` in a terminal window, you will find out the rest
- for GTK+ version execute `./run-gtk.py`
- for extended application window execute `./run-player.py`
- for standalone timelapse calculator run `./run-tlcalc.py`

I HAVE SOME IDEAS.
YOUR CODE NEEDS SOME IMPROVEMENTS.
YOU SPELLED XYZ WRONG!

- feel free to contact me or file an issue but be patient I'm a bloody rookie

BUT WAIT - THERE IS MORE!

- there are 2 additional scripts which only help me getting localization done and can be easily ignored. fyi:
  - herostuff/localizeorcry.py:     wraps new strings for gettext recognition in the source files (code and glade) and updates translation template and existing po files
  - herostuff/po/update_mo.py:      updates all mo files, only needed when translated strings are added to po files

SCREENSHOTS!

- [Click](screenshots/)

![Player window v0.4](screenshots/window_player_v0.4.png)
