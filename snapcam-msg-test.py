#!/usr/bin/env python3
from collections import OrderedDict as OD
from Snapcam import Snapcam, settings
from test_util import pp

scams = [
    Snapcam("d4:2c:3d:05:ce:f5", debug=True),
    Snapcam("d4:2c:3d:05:dc:e0", debug=True),
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
    pp("CAMERA: {}".format(sc.ble_mac), color="green")
    for item in items:
        pp(sc.query_item(item))
        pp(sc.query_item("mode"))

    for cmd in cmds:
        pp(sc.send_msgs(cmd, expect_rsp=False))

    sc.disconnect()
