from .hardware_lcd import GpioLcd
from .hardware_keypad import Keypad
from .hardware_config import ConfigManager
from utime import time, sleep_ms
import machine
from ..characters import CustomCharacters


class HardwareImplementation:
    CONFIG_FILENAME = "config.json"

    def __init__(self, keypad_row_pins, keypad_col_pins, display_pins):
        self.keypad_row_pins = keypad_row_pins
        self.keypad_col_pins = keypad_col_pins
        self.display_pins = display_pins

        self.config_manager = ConfigManager(HardwareImplementation.CONFIG_FILENAME)

        self.keypad = Keypad(keypad_row_pins, keypad_col_pins)
        self.make_display()

    def config_read(self, key):
        return self.config_manager.read(key)

    def config_write(self, key, value):
        self.config_manager.write(key, value)

    def blink_cursor_at(self, i, j):
        self.display.move_to(i, j)
        self.display.blink_cursor_on()

    def cursor_off(self):
        self.display.hide_cursor()

    def make_display(self):
        self.display_off()
        sleep_ms(10)
        self.display_pins["RS"].low()
        self.display_pins["EN"].low()
        self.display_pins["D4"].low()
        self.display_pins["D5"].low()
        self.display_pins["D6"].low()
        self.display_pins["D7"].low()
        self.display_pins["BL"].high()
        self.display = GpioLcd(
            self.display_pins["RS"],
            self.display_pins["EN"],
            self.display_pins["D4"],
            self.display_pins["D5"],
            self.display_pins["D6"],
            self.display_pins["D7"],
        )

        for character in CustomCharacters.CHARACTERS:
            self.display.custom_char(character["index"], character["bytes"])

    def sleep_callback_reset(pin):
        machine.reset()

    def set_sleep(self):
        self.display_off()
        for p in self.keypad_row_pins:
            p.low()

        for p in self.keypad_col_pins:
            p.irq(
                handler=HardwareImplementation.sleep_callback_reset,
                trigger=machine.Pin.IRQ_RISING,
            )

        for p in self.keypad_row_pins:
            p.high()

        machine.deepsleep()

    def write_text(self, text, i, j):
        if self.display is None:
            self.make_display()
        self.display.writestr(text, i, j)

    def clear_display(self):
        if self.display is None:
            self.make_display()

        self.display.clear()

    def display_on(self):
        if self.display is None:
            self.make_display()

    def display_off(self):
        self.display_pins["RS"].high()
        self.display_pins["EN"].high()
        self.display_pins["D4"].high()
        self.display_pins["D5"].high()
        self.display_pins["D6"].high()
        self.display_pins["D7"].high()
        self.display_pins["BL"].low()
        self.display = None

    def get_time(self):
        return time()

    def read_key(self):
        return self.keypad.read_key()
