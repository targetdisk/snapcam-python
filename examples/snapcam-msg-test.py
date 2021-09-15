#!/usr/bin/env python3
from collections import OrderedDict as OD
from Snapcam.btle import settings, Snapcam
from Snapcam.util import cprint

scams = [
    Snapcam("d4:2c:3d:05:ce:f5", debug=True),
    Snapcam("d4:2c:3d:05:dc:e0", debug=True),
    Snapcam("d4:2c:3d:07:44:60", debug=True),
]

items = ["ver", "wifi"]

our_settings = [
    ("AutoRotation", "On"),
    ("second", 10),
    ("VideoMode", "720P"),
    ("PhotoMode", "8MP"),
]
cmds = []
for setting in our_settings:
    cmds += (OD([("Type", settings[setting[0]]), (setting[0], setting[1])]),)

for sc in scams:
    sc.connect()
    cprint("CAMERA: {}".format(sc.ble_mac), color="green")
    for item in items:
        cprint(sc.query_item(item))
        cprint(sc.query_item("mode"))

    for cmd in cmds:
        cprint(sc.send_msgs(cmd, expect_rsp=False))

    sc.disconnect()
