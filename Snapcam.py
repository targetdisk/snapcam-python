from bluepy import btle as bt
from pprint import PrettyPrinter
import typing

pp = PrettyPrinter(indent=4).pprint
last_notification = []

def eprint(errmsg):
    """Prints `errmsg` to STDERR."""
    print(errmsg, file=STDERR)


class Snapcam:
    btch = {}
    btsvc = {}

    long_notification_ops = {
        0: [0x2D, b'\xffb{"Type":25}CRC:f'],
        2: [0x2D, b'{"ret":1}'],
        3: [0x2D, b'{"ret":1}'],
        4: [0x2D, b'\xffb{"Type":28}CRC:2'],
        6: [0x2D, b'{"ret":1}'],
        7: [0x2D, b'{"ret":1}'],
        8: [0x2D, b'\xffb{"Type":33}CRC:e'],
        9: [0x2D, b'\xffb{"Type":22}CRC:c'],
        10: [0x2D, b'\xff1e{"Type":1,"AutoRo'],
        11: [0x2D, b'tation":"On"}CRC:d'],
        12: [0x2D, b'\xff19{"Type":11,"secon'],
        13: [0x2D, b'd":"10"}CRC:5'],
        14: [0x2D, b'\xff1c{"Type":5,"PhotoM'],
        15: [0x2D, b'ode":"2MP"}CRC:9'],
        16: [0x2D, b'\xff1d{"Type":4,"VideoM'],
        17: [0x2D, b'ode":"720P"}CRC:f'],
        18: [0x2D, b'\xff23{"Type":15,"time"'],
        19: [0x2D, b':"20210907182137"}CR'],
        20: [0x2D, b"C:6"],
        21: [0x2D, b'\xffb{"Type":27}CRC:1'],
        23: [0x2D, b'{"ret":1}'],
        24: [0x2D, b'\xffb{"Type":24}CRC:e'],
        26: [0x2D, b'{"ret":1}'],
        25: [0x2D, b'{"ret":1}'],
        26: [0x2D, b'\xffb{"Type":18}CRC:1'],
        28: [0x2D, b'{"ret":1}'],
        29: [0x2D, b'{"ret":1}'],
    }

    notification_ops = {
        0: [0x2D, b'\xffb{"Type":18}CRC:1'],
        2: [0x2D, b'{"ret":1}'],
        3: [0x2D, b'{"ret":1}'],
    }

    def __init__(self, ble_mac: str):
        self.ble_mac = ble_mac

    def mk_crc(self, msg: bytes):
        sum = 0
        for byte in msg:
            sum += byte

        return ("CRC:" + hex(sum & 15)[2:]).encode("ascii")

    def send_msg(self, msg: bytes):
        pass

    def send_cmd(self, msg: bytes, chr_handle: int=0x2D):
        if len(msg) > 18:
            msg = (
                b"\xff" + hex(len(msg))[2:].encode("ascii") + msg + mk_crc(msg)
            )
            msgs = [msg[i + 20] for i in range(0, len(msg), 20)]
            for msg in msgs:
                self.btch[chr_handle].write(msg)

        else:
            prefix = b"\xffb"

    def do_btch_write(self, not_count):
        try:
            characteristic = self.notification_ops[not_count][0]
            data = self.notification_ops[not_count][1]
            print(
                "{}: [{}]: Writing: {}".format(
                    not_count, hex(characteristic), data
                )
            )
            self.btch[characteristic].write(data)
        except KeyError:
            print("Waiting...")

    class Delegate_2a(bt.DefaultDelegate):
        def __init__(self, params=None):
            bt.DefaultDelegate.__init__(self)

        def handleNotification(chandle, data):
            print("handle: {}".format(hex(chandle)), end="  ")
            print("data:", end=" ")
            pp(data)
            last_notification = [chandle, data]

    def start_wifi(self, ssid: str = "SnapCam_6A6C"):
        pass

    def pkg_chrs(self, _chrs: bt.Characteristic):
        chrs = {}
        for c in _chrs:
            chrs[c.getHandle()] = c

        return chrs

    def connect(self):
        self.btp = bt.Peripheral(self.ble_mac)
        self.btch = self.pkg_chrs(self.btp.getCharacteristics())

        for s in self.btp.getServices():
            self.btsvc[s.uuid] = self.btp.getServiceByUUID(s.uuid)

        self.btp.setDelegate(self.Delegate_2a)

    def show_services(self):
        for su, svc in self.btsvc.items():
            print("{} (".format(su.binVal.hex()) + su.getCommonName() + "):")
            self._show_characteristics(self.pkg_chrs(svc.getCharacteristics()))

    def show_characteristics(self):
        print("ALL CHARACTERISTICS:")
        self._show_characteristics(self.btch)

    def _show_characteristics(self, chars: dict):
        for handle, c in chars.items():
            print("  handle: " + hex(handle), end="  ")
            print("  " + c.propertiesToString())

    def start_notifications(self):
        pass

    def disconnect(self):
        self.btp.disconnect()
