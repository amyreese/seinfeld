# Copyright 2014 John Reese
# Licensed under the MIT license

import os
from os import path
import sys

cwd = path.abspath(path.dirname(__file__))
sys.path.insert(0, cwd)

libpath = path.join(cwd, "lib")
libs = ["flask",
        "jinja2",
        "werkzeug",
        "python-memcached-1.48",
        ]

for lib in libs:
    sys.path.insert(0, path.join(libpath, lib))

os.environ['APP_PATH'] = cwd

from core import app as application
import views

if __name__ == '__main__':
    print "debug shell"

    print ">>> from core import app"
    from core import app
