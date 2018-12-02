#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from herostuff import modules

try:
    modules.app.main(sys.argv)
except EOFError:
    raise
finally:
    print("The End Is Nigh!")
