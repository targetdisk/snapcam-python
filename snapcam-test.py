from pprint import PrettyPrinter
from Snapcam import Snapcam, last_notification

pp = PrettyPrinter(indent=4).pprint

#sc = Snapcam("d4:2c:3d:05:dc:e0")
sc = Snapcam("d4:2c:3d:05:ce:f5")
sc.connect()

sc.show_characteristics()
sc.show_services()
print("0x2a read() = " + sc.btch[0x2A].read().hex())

notifications = [0, True]
while True:
    if notifications[1]:
        sc.do_btch_write(notifications[0])
        notifications[1] = False

    if sc.btp.waitForNotifications(20.0):
        notifications[0] += 1
        notifications[1] = True

    #if notifications[0] == 4:
    if notifications[0] == 30:
        break
