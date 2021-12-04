#!/usr/bin/env python3
from Snapcam.connector import SnapcamRTSP

scr = SnapcamRTSP(debug=True)
scr.stream()
