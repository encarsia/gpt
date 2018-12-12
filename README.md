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


### INSTALLATION

 * download and extract or clone repository and change into said folder
 
> FTR: when executing `python`, it is Python 3
 
### ARE WE THERE YET?

 * execute `run.py`
 * if you intend to use the desktop icon, edit `data/GPT.desktop` and customize path of "Exec", and "Icon" and copy file to `~/.local/share/applications/`

### I'M LAZY!

 * run `python setup.py install --user` to install the app just for the current user or
 * run `python setup.py build` and then `python setup.py install` with administrator privilege for system-wide installation
 * press the <kbd>SUPER</kbd> key and start typing <kbd>G</kbd>...<kbd>P</kbd>...<kbd>T</kbd>...<kbd>ENTER</kbd>

### HOW DO I GET RID OF THIS?

 * Lucky you asked. If you installed the application via `setup.py`, run `python setup.py uninstall --user` or `python setup.py uninstall` (with superuserpowers) to undo the installation. This will remove the Python package and any desktop files.

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

![Default application window v0.5](data/screenshots/win_v0.5.png)

#### Compact view

![Compact view v0.5](data/screenshots/compact_v0.5.png)

#### CLI

![CLI v0.5](data/screenshots/cli_v0.5.png)

### SOURCES AND LICENSES

* application: [GNU General Public License v3](LICENSE.md)
* icon: [Action camera by Green](https://thenounproject.com/term/action-camera/207962/) from the [Noun Project](https://thenounproject.com/), licensed under [Creative Commons Attribution (CC BY)](https://creativecommons.org/licenses/by/3.0/)