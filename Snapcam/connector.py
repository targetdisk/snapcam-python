from multiprocessing import Process, Queue
from Snapcam.rtsp_util import digest_pkts, get_sessid, get_bindip
from Snapcam.util import eprint, get_nthreads
import socket
import typing
from time import sleep


class SnapcamRTSP:
    def send_setup(self):
        self.cmd_sock.send(
            bytes(
                "SETUP "
                + self.cam_addr.decode("ascii")
                + "/trackID=1 RTSP/1.0\r\nCSeq: 3\r\nUser-Agent: python\r\n"
                + "Transport: RTP/AVP;unicast;client_port="
                + str(self.rx_ports[0])
                + "-"
                + str(self.rx_ports[1])
                + "\r\n\r\n",
                "ascii",
            )
        )
        return self.cmd_sock.recv(4096)

    def __init__(
        self,
        rx_ports: (int, int) = (60784, 60785),
        rx_timeout: int = 5,
        cam_ip: str = "192.168.2.103",
        cam_port: int = 554,
        debug: bool = False,
    ):
        self.rx_ports = rx_ports
        self.rx_timeout = rx_timeout
        self.cam_ip = cam_ip
        self.cam_port = cam_port
        self.cam_addr = b"rtsp://" + bytes(self.cam_ip, "ascii")
        self.debug = debug

        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cmd_sock.settimeout(self.rx_timeout)

        self.rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rx_sock.settimeout(self.rx_timeout)

        self.cmd_sock.connect((self.cam_ip, self.cam_port))

        rsp = self.send_setup()
        if self.debug is True:
            print(rsp.decode())

        self.sessid = get_sessid(rsp)
        self.rx_sock.bind((get_bindip(self.cam_ip), self.rx_ports[0]))

    def send_play(self):
        while True:
            self.cmd_sock.send(
                bytes(
                    "PLAY "
                    + self.cam_addr.decode("ascii")
                    + " RTSP/1.0\r\nCSeq: 5\r\nUser-Agent: python\r\n"
                    + "Session: "
                    + str(self.sessid)
                    + "\r\nRange: npt=0.000-\r\n\r\n",
                    "ascii"
                )
            )

            rsp = self.cmd_sock.recv(4096)
            if self.debug is True:
                print(rsp.decode())

            sleep(5)

    def get_pkts(self):
        while True:
            try:
                self.pkt_q.put(self.rx_sock.recv(4096))
            except self.socket.timeout:
                if self.rx_timeout is not None:
                    eprint(
                        "[WARN]: Timed out reading on rx_sock after "
                        + "{} seconds.".format(self.rx_timeout)
                    )
                else:
                    eprint("[WARN]: Timed out reading on rx_sock!")

    def stream(self):
        self.pkt_q = Queue(maxsize=8192)
        self.write_q = Queue(maxsize=8192)

        player = Process(target=self.send_play)
        getter = Process(target=self.get_pkts)
        stomach = Process(target=digest_pkts, args=(self.pkt_q, self.write_q))

        player.start()
        getter.start()
        stomach.start()

        while True:
            sleep(1)
