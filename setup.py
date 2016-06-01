#!/usr/bin/env python

from distutils.core import setup

setup(name="drawbotPlotter",
    version="0.1",
    description="Plotter support for DrawBot.",
    author="Jens Kutilek, Bernd Volmer",
    url="https://github.com/jenskutilek/DrawBotPlotter",
    license="Internal use only",
    packages=[
        "drawbotPlotter",
    ],
    package_dir={"":"Lib"}
)
