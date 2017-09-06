#!/usr/bin/env python
# -*- coding: utf-8 -*-

import herostuff.modules

try:
    herostuff.modules.app.load_application_window()
    herostuff.modules.app.main()
except EOFError:
    raise
finally:
    print("The End Is Nigh!")

#TODO show message dialog while creating timelapse
#TODO eject/unmount card
#TODO player window: create timelapse on single videos
#TODO make correct use of gtk application
