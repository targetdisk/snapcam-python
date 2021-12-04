from multiprocessing import Process, Queue
#from SnapcamBits import call_test, hello_world, queue_test
from SnapcamBits import *
import typing
from time import sleep


def stream_file(rq: Queue):
    file = open("stream.ts", "rb")
    while True:
        pkt = file.read(4096)
        if len(pkt) == 0:
            file.close()
            break
        rq.put(pkt)
    rq.close()


def print_q(tq: Queue):
    while not tq.empty():
        print(tq.get())


def spam():
    print("eggs")


class Hello:
    def hello(self):
        print("Hello method!")


hello_obj = Hello()

hello = Process(target=hello_world)
hello_method = Process(target=mcall_test, args=(hello_obj,))

#hello.start()
#hello_method.start()

read_q = Queue(maxsize=8192)
test_q = Queue(maxsize=8192)

getter = Process(target=stream_file, args=(read_q,))
qtest = Process(target=queue_test, args=(read_q, test_q))
printer = Process(target=print_q, args=(read_q,))

getter.start()
while read_q.empty():
  sleep(0.5)
#printer.start()
qtest.start()
