from setuptools import setup, Extension
from Snapcam.util import runcmd

try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

# install_requires breaks installing bluepy.  I don't know why and I really
# don't care, so I did this:
pipmain(["install", "-r", "requirements.txt"])

scripts = ["scripts/enable-sc-wifi"]
scb_srcs = ["Snapcam/bits/scb.c"]
scb_deps = ["Snapcam/bits/scb.h"]
inc_dirs = runcmd("helpers/include_info -P").splitlines()

scb_m = Extension(
    name="SnapcamBits",
    sources=scb_srcs,
    include_dirs=inc_dirs,
    depends=scb_deps,
)

setup(
    name="Snapcam",
    version="0.1",
    author="Andrea Rogers (@targetdisk.io)",
    author_email="targetdisk one three nine four at g mail dot com",
    url="https://github.com/targetdisk/snapcam-python",
    packages=["Snapcam"],
    include_package_data=True,
    scripts=scripts,
    ext_modules=[scb_m],
)
