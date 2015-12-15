#!/usr/bin/env python
import serial
import time


class LEDArray():
    def __init__(self, orderdata):
        # Who do you think you are?
        self.orderdata = orderdata