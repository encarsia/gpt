#!/usr/bin/env python
# -*- coding: utf-8 -*-

import herostuff.modules

try:
    herostuff.modules.tlc.standalone()
    herostuff.modules.app.main()
except EOFError:
    raise
finally:
    print("The End Is Nigh!")
