class Key:
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    CLEAR = 10
    ENTER = 11
    POWER = 12
    CONFIG = 13
    PERCENT = 14
    UNIT = 15
    TIMEOUT = -1

    LABELS = {
        ZERO: "0",
        ONE: "1",
        TWO: "2",
        THREE: "3",
        FOUR: "4",
        FIVE: "5",
        SIX: "6",
        SEVEN: "7",
        EIGHT: "8",
        NINE: "9",
        CLEAR: "CLR",
        ENTER: "=",
        POWER: "P",
        CONFIG: "SET",
        PERCENT: "%",
        UNIT: "KG/LB",
    }

    def is_numeric(key):
        return Key.ZERO <= key <= Key.NINE


class Interface:
    KEYPAD_LAYOUT = [
        [Key.ONE, Key.TWO, Key.THREE, Key.POWER],
        [Key.FOUR, Key.FIVE, Key.SIX, Key.CONFIG],
        [Key.SEVEN, Key.EIGHT, Key.NINE, Key.PERCENT],
        [Key.CLEAR, Key.ZERO, Key.ENTER, Key.UNIT],
    ]

    DISPLAY_DIMS = (2, 16)
    KEYPAD_DIMS = (len(KEYPAD_LAYOUT), len(KEYPAD_LAYOUT[0]))

    def __init__(self, implementation):
        self.display_power = True
        self.implementation = implementation

    def config_read(self, key):
        return self.implementation.config_read(key)

    def config_write(self, key, value):
        self.implementation.config_write(key, value)

    def write_text(self, text, i, j):
        if (
            i < 0
            or j < 0
            or i >= Interface.DISPLAY_DIMS[0]
            or j >= Interface.DISPLAY_DIMS[1]
        ):
            raise ValueError()

        if self.display_power:
            self.implementation.write_text(text, i, j)

    def blink_cursor_at(self, i, j):
        self.implementation.blink_cursor_at(i, j)

    def cursor_off(self):
        self.implementation.cursor_off()

    def clear_display(self):
        self.cursor_off()
        self.implementation.clear_display()

    def read_key(self, timeout=60):
        end_time = self.implementation.get_time() + timeout
        key = None

        while key is None and self.implementation.get_time() <= end_time:
            key = self.implementation.read_key()

        if key is not None:
            return key
        return Key.TIMEOUT

    def set_sleep(self):
        self.implementation.set_sleep()

    def toggle_display(self):
        if self.display_power:
            self.display_off()
        else:
            self.display_on()

    def display_on(self):
        self.display_power = True
        self.implementation.display_on()

    def display_off(self):
        self.display_power = False
        self.implementation.display_off()
