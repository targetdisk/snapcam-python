from setuptools import setup
try:
    from pip import main as pipmain
except ImportError:
    from pip._internal import main as pipmain

pipmain(["install", "-r", "requirements.txt"])

scripts = ["scripts/enable-sc-wifi"]
setup(
    name="Snapcam",
    version="0.1",
    author="Andrea Rogers (@targetdisk.io)",
    author_email="targetdisk one three nine four at g mail dot com",
    url="https://github.com/targetdisk/snapcam-python",
    packages=["Snapcam"],
    include_package_data=True,
    scripts=scripts,
)
