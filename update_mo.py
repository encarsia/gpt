#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

os.chdir(os.path.join('herostuff', 'po'))

for f in os.listdir():
    if f.endswith('.po'):
        newmo = open(os.path.join('locale',f[:2],'LC_MESSAGES','GPT.mo'),'w')
        subprocess.run(['msgfmt','--output',os.path.join('locale',f[:2],'LC_MESSAGES','GPT.mo'),f])
        print("%s: updated %s" % (f,os.path.join('locale',f[:2],'LC_MESSAGES','GPT.mo')))
        newmo.close()
