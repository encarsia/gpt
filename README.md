### WHAT IS THIS?

- a simple tool for organizing your GoPro stuff

### WHAT IS IT NOT?

- a video editor
- professional

### TELL ME ABOUT FEATURES!

- import your stuff from SD card
- rename files in a more logical order than according to the GoPro naming convention
- overview of your footage, directly rename folders
- create timelapse videos from your stuff via FFmpeg
- localization: English, German
- open older content as Kdenlive project
- extended application window with fancy video preview and media information (requires GStreamer and MediaInfo)

### YOU MUST BE JOKING!

- well, these are the basic tasks I usually perform before doing the video editing in Kdenlive (use it, it's great)
- I'm thinking about polishing and new features but no warranty that this will get any better

### WHAT ABOUT SYSTEM REQUIREMENTS?

- Python 3 bindings for GObject
- FFmpeg (optional)
- GStreamer and MediaInfo for the extended application window
- GoPro camera

### HOW DO I GET THIS THING TO WORK ON MY MACHINE?

(add installation guide here)


### HOW DO I USE IT?

* execute `run.py`, this will load the default application window with media preview
* these commandline options are available (run `run.py --help`:

```txt
  -v, --version               Show version info
  --default                   Default GUI with integrated view switch
  -c, --alt-gui-compact       Altenative GUI, compact view
  -e, --alt-gui-ext           Alternative GUI, extended view (GStreamer preview)
  --cli                       Commandline interface
  -t, --tl-calc               Run the timelapse calculator
```

### I HAVE SOME IDEAS.
### YOUR CODE NEEDS SOME IMPROVEMENTS.
### YOU SPELLED XYZ WRONG!

- feel free to contact me or file an issue but be patient I'm a bloody rookie

### SCREENSHOTS!

#### Default application window

![Default application window v0.5](screenshots/win_v0.5.png)

#### Compact view

![Compact view v0.5](screenshots/compact_v0.5.png)

#### CLI

![CLI v0.5](screenshots/cli_v0.5.png)
