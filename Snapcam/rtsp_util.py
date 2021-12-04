from multiprocessing import Queue
from os import path as ospath
import re
from Snapcam.util import cprint, eprint, runcmd
# import SnapcamBits as scb
import socket
from subprocess import run
import typing

cwd = ospath.abspath(ospath.curdir)


def get_sessid(rsp: bytes):
    """Search session ID from RTSP strings"""
    for line in rsp.decode().split("\r\n"):
        ss = line.split()
        if ss[0].strip() == "Session:":
            return int(ss[1].split(";")[0].strip())


def get_bindip(cam_ip: str = "192.168.2.103"):
    """
    Get IP of SnapCam WiFi connection to bind UDP port to.
    (Currently assumes /24 subnet and only one SnapCam NIC.)
    """
    subnet = ".".join(cam_ip.split(".")[:-1]) + ".0/24"

    for line in runcmd("ip r").decode().split("\n"):
        words = re.split(r"\s+", line)
        if words[0] == subnet:
            for i in range(len(words)):
                if words[i] == "src":
                    return words[i + 1]

    return None


def digest_pkts(pkt_q: Queue, write_q: Queue):
    """
    Stubbed writer for now, will be replaced by C Extension using write_q later.
    """
    runcmd("rm -f " + cwd + "/play")
    runcmd("mkfifo " + cwd + "/play")

    demopipe = open("play", "ab")
    while True:
        try:
            demopipe.write(pkt_q.get())
        except Exception:
            break


def v4ldump():
    run(
        "ffmpeg -i " + cwd + "/play "
        + "-f v4l2 -c:v rawvideo -pix_fmt yuv420p -r 60 /dev/video4",
        shell=True,
    )
