from Snapcam.connector import SnapcamRTSP
from Snapcam.util import cprint, eprint, lilprint

scr = SnapcamRTSP(debug=True)
scr.stream()
