from machine import Pin
from utime import sleep_ms
from ..interface import Interface


class Keypad:
    def __init__(self, rowpins, colpins):
        self.rows = rowpins
        self.cols = colpins

        for rowpin in self.rows:
            rowpin.init(Pin.OUT)
            rowpin.low()
        for colpin in self.cols:
            colpin.init(Pin.IN, pull=Pin.PULL_DOWN)

    def wait_up(self, col):
        while not self.check_cell_db(col, desired=0, time_betw=2, intervals=10):
            pass

    def check_cell_db(self, col, desired=1, time_betw=2, intervals=10):
        # assume row is set to high
        for i in range(intervals):
            if self.cols[col].value() != desired:
                return False
            sleep_ms(time_betw)
        return True

    def read_key(self):
        for row in range(len(self.rows)):
            self.rows[row].high()
            for col in range(len(self.cols)):
                if self.check_cell_db(col):
                    self.wait_up(col)
                    self.rows[row].low()
                    return Interface.KEYPAD_LAYOUT[row][col]
            self.rows[row].low()
        return None
