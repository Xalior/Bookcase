#!/usr/bin/env python
import serial
import time


class TTYRelay():
    def __init__(self, port):
        # I am Port
        self.port = port
        # 4 relays, all default to off...
        self.status = ['0', '0', '0', '0']
        # open the requested USB TTY
        self.fd = serial.Serial("/dev/ttyUSB"+str(self.port), 9600)
        # pretend to be Windows App...
        self.fd.write('\x50')
        # tell it you're switching to commandmode
        self.fd.write('\x51')
        self.write()

    def on(self, index=None):
        if index is None:
            self.status = ['1', '1', '1', '1']
        else:
            self.set(index, 1)

    def off(self, index=None):
        if index is None:
            self.status = ['0', '0', '0', '0']
        else:
            self.set(index, 0)

    def set(self, index, bit):
        self.status[index] = str(bit)

    def write(self):
        self.fd.write('0x%02X' % int(''.join(self.status), 2))

    def demo(self):
        # turn them all off
        self.off()
        self.write()
        time.sleep(1)
        # turn _only_ #1 on
        self.on(0)
        self.write()
        time.sleep(1)
        # turn _only_ #2 on
        self.off()
        self.on(1)
        self.write()
        time.sleep(1)
        # turn _only_ #3 on
        self.off()
        self.on(2)
        self.write()
        time.sleep(1)
        # turn _only_ #4 on
        self.off()
        self.on(3)
        self.write()
        time.sleep(1)
        # turn them all on
        self.on()
        time.sleep(1)
        # and goodnight...
        self.off()
