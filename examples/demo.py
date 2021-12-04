#!/usr/bin/env python3
from json import dumps
from Snapcam.btle import Snapcam
from Snapcam.util import cprint
from time import sleep

# Initialize a Snapcam object with debug printing turned on.
sc = Snapcam("d4:2c:3d:07:44:60", debug=True)

# Pair and connect to our SnapCam.
sc.connect()

# Get running SnapCam firmware revision
cprint(sc.query_item("ver"))

# Set some settings
sc.set_settings(
    [
        ("AutoRotation", "On"),
        ("second", 10),
        ("VideoMode", "720P"),
        ("PhotoMode", "8MP"),
    ]
)

sc.disconnect()
sleep(5)

# Enable wifi
cprint(dumps(sc.enable_wifi()))
