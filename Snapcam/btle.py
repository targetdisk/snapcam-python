from bluepy import btle as bt
from collections import OrderedDict as OD
import json as j
import re
from Snapcam.exceptions import *
from Snapcam.util import pp, eprint, cprint
import typing


settings = {
    "AutoRotation": 1,
    "VideoMode": 4,
    "PhotoMode": 5,
    "second": 11,
    "time": 15,
}


class Snapcam:
    btch = {}
    btsvc = {}
    cam_settings = {}
    cfg_settings = {}
    last_notification = []

    toggles = {
        "touchpad": 33,
        "wifi": 22,
    }

    queries = {
        "ver": 25,
        "mode": 28,
        "touchpad": 28,
        "status": 28,
        "battery": 27,
        "storage": 24,
        "total": 24,
        "free": 24,
        "wifi": 18,
        "psk": 18,
        "ssid": 18,
    }

    def __init__(
        self,
        ble_mac: str,
        noti_timeout: float = 2.0,
        debug: bool = False,
        do_color: bool = True,
    ):
        self.ble_mac = ble_mac
        self.noti_timeout = noti_timeout
        self.J = j.JSONEncoder(
            skipkeys=False,
            ensure_ascii=True,
            check_circular=True,
            allow_nan=False,
            sort_keys=False,
            indent=None,
            separators=(",", ":"),
        )
        self.debug = debug
        self.do_color = do_color

    def att_write(self, msg: bytes, chr_handle: int = 0x2D):
        if self.debug is True:
            print("[WRITE]        [{}]: {}".format(hex(chr_handle), msg))

        self.btch[chr_handle].write(msg)

    def mk_crc(self, msg: bytes):
        sum = 0
        for byte in msg:
            sum += byte

        return ("CRC:" + hex(sum & 15)[2:]).encode("ascii")

    def mk_msgs(self, cmd: OD, chr_handle: int = 0x2D):
        if self.debug:
            print("\nSending:", end=" ")
            cprint(cmd, color="green", do_color=self.do_color)
        msg = self.J.encode(cmd).encode("ascii")

        if len(msg) > 18:
            msg = (
                b"\xff"
                + hex(len(msg))[2:].encode("ascii")
                + msg
                + self.mk_crc(msg)
            )
            msgs = [msg[i : i + 20] for i in range(0, len(msg), 20)]
        else:
            msgs = [b"\xffb" + msg + self.mk_crc(msg)]

        return msgs

    def get_notification(self):
        if self.btp.waitForNotifications(self.noti_timeout):
            return self.last_notification[1]
        else:
            return None

    def ask_retransmit(self, chr_handle: int = 0x2D):
        self.att_write(b'{"ret":0}', chr_handle)
        return self.get_notification()

    def parse_fail(self, msg: bytes):
        raise SnapCamParserError("Failed to parse {}".format(msg))

    def send_ack(self, chr_handle: int = 0x2D):
        self.att_write(b'{"ret":1}', chr_handle)
        return self.get_notification()

    def json_fixup(self, msg: bytes):
        new_jbytes = b""
        num_rx = re.compile(r":[0-9 ]+[,}]".encode("ascii"))
        for match in num_rx.finditer(msg):
            new_jbytes += msg[: match.span(0)[0]] + re.sub(
                b"\\s", b"", match.group(0)
            )
            match_end = match.span(0)[1]
        new_jbytes += msg[match_end:]

        return j.loads(new_jbytes)

    def parse_ack(self, msg: bytes):
        try:
            return j.loads(msg)
        except j.JSONDecodeError:
            return self.json_fixup(msg)

    def get_multipart_msg(self, rsp: bytes, chr_handle: int = 0x2D):
        json_begin = rsp.find(b"{")
        if json_begin == -1:
            eprint("ERROR: Couldn't find JSON open!!!", do_color=self.do_color)
            self.parse_fail(rsp)

        expected_length = int(rsp[1:json_begin], 16)
        big_rsp = rsp[json_begin:]

        while len(big_rsp) < (expected_length + 5):
            (attempt, rsp) = (0, None)
            while rsp is None:
                if attempt == 3:
                    raise SnapCamBluetoothReceiveError(
                        "Couldn't read packet after three attempts!"
                    )
                rsp = self.send_ack(chr_handle)
                attempt += 1

            big_rsp += rsp

        json_end = big_rsp.rfind(b"}") + 1
        crc = re.sub(b"\\s", b"", big_rsp[json_end:])
        return (big_rsp[:json_end], crc)

    def parse_rsp(self, rsp: bytes, chr_handle: int = 0x2D):
        crc_match = True

        for attempt in range(0, 3):
            if rsp[0] not in (0xFF, 0x7B):
                rsp = self.ask_retransmit(chr_handle)
            else:
                break

            if attempt == 2 and rsp[0] not in (0xFF, 0x7B):
                self.parse_fail(rsp)

        if rsp[0] == 0xFF:
            (jbytes, crc) = self.get_multipart_msg(
                rsp=rsp, chr_handle=chr_handle
            )

        else:
            crc = re.sub(b"\\s", b"", rebig_rsp[rsp.rfind(b"}") + 1 :])

        our_crc = self.mk_crc(jbytes)
        if our_crc != crc:
            eprint(
                "WARN: CRC mismatch on multipart data!  "
                + "Theirs: {}. Computed: {}".format(crc, our_crc),
                do_color=self.do_color,
            )
            crc_match = False

        try:
            return (j.loads(jbytes), crc_match)
        except j.JSONDecodeError:
            try:
                return (self.json_fixup(jbytes), crc_match)
            except UnicodeDecodeError as e:
                eprint(
                    "ERROR: Couldn't parse message: {}".format(jbytes),
                    do_color=self.do_color,
                )
                return {"exception": e, "unparsed_rsp": jbytes}

    def send_msgs(
        self, cmd: OD, chr_handle: int = 0x2D, expect_rsp: bool = True
    ):
        """If fails, returns None instead of tuple of (dict, bool)"""
        msgs = self.mk_msgs(cmd=cmd, chr_handle=chr_handle)

        for i in range(0, len(msgs)):
            for send_attempt in range(0, 3):
                self.att_write(msgs[i], chr_handle)
                ack = self.parse_ack(self.get_notification())
                try:
                    if expect_rsp and (ack["Type"] != cmd["Type"]):
                        raise TypeError(
                            "Expected response of Type {}, got {}".format(
                                cmd["Type"], ack["Type"]
                            )
                        )
                except KeyError:
                    eprint(
                        'WARN: Received ack of unknown "Type"',
                        do_color=self.do_color,
                    )
                try:
                    ret = ack["ret"]
                except KeyError:
                    for key in ack.keys():
                        ack[key.replace(" ", "")] = ack.pop(key)

                ret = ack["ret"]
                if ret == 1:
                    break
                elif ret == 0:
                    continue
                else:
                    raise ValueError(
                        'Expected a "ret" of 1 or 0, but got {}'.format(
                            ack["ret"]
                        )
                    )
            if i == 2 and ret != 1:
                raise SnapCamBluetoothSendError(
                    "Tried three times to send message ({})".format(msg)
                    + ", but still got nonzero return from SnapCam."
                )
        if expect_rsp:
            for send_attempt in range(0, 3):
                rsp = self.get_notification()
                if rsp:
                    break
            if rsp is not None:
                return self.parse_rsp(rsp=rsp, chr_handle=chr_handle)
            else:
                return None
        else:
            return None

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

        self.btd = SnapCamDelegate(parent=self, debug=self.debug)
        self.btp.setDelegate(self.btd)

        if self.debug is True:
            print("0x2a read() = " + self.btch[0x2A].read().hex())

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

    def disconnect(self):
        try:
            self.btp.disconnect()
        except AttributeError:
            eprint("Can't disconnect, not connected!", do_color=self.do_color)

    def query_item(
        self, item: str, expect_rsp: bool = True, chr_handle: int = 0x2D
    ):
        try:
            sc_type = self.queries[item]
        except KeyError:
            eprint("ERROR: unknown query!", do_color=self.do_color)
            return None

        return self.send_msgs(
            cmd=OD([("Type", sc_type)]), expect_rsp=expect_rsp
        )

    def toggle_item(
        self, item: str, expect_rsp: bool = False, chr_handle: int = 0x2D
    ):
        try:
            sc_type = self.toggles[item]
        except KeyError:
            eprint("ERROR: unknown query!", do_color=self.do_color)
            return None

        return self.send_msgs(
            cmd=OD([("Type", sc_type)]), expect_rsp=expect_rsp
        )

    def enable_wifi(self, chr_handle: int = 0x2D):
        disconnect_bt = False

        if not hasattr(self, "btp"):
            self.connect()
            disconnect_bt = True

        self.toggle_item("wifi")
        wifi_info = self.query_item("wifi")

        if disconnect_bt is True:
            self.disconnect()

        return wifi_info[0]


class SnapCamDelegate(bt.DefaultDelegate):
    def __init__(self, parent: Snapcam, debug: bool = False):
        self.parent = parent
        self.debug = debug
        bt.DefaultDelegate.__init__(self)

    def handleNotification(self, chandle, data):
        if self.debug is True:
            print("[NOTIFICATION] [{}]".format(hex(chandle)), end=": ")
            pp(data)

        self.parent.last_notification = [chandle, data]
