#!/usr/bin/env python
# -*- coding: utf-8 -*-

import herostuff.modules

try:
    herostuff.modules.app.get_window_content()
    herostuff.modules.app.main()
except EOFError:
    pass
print("The End Is Nigh!")
