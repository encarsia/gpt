#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import modules

try:
    modules.app.main(sys.argv)
except EOFError:
    raise
