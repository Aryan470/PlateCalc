import PySimpleGUI as sg
from time import time
from .interface import Interface, Key

keypad_buttons = [
    [
        Key.LABELS[Interface.KEYPAD_DIMS[1] * i + j]
        for j in range(Interface.KEYPAD_DIMS[1])
    ]
    for i in range(Interface.KEYPAD_DIMS[0])
]
max_by_col = [
    max([len(keypad_buttons[r][c]) for r in range(Interface.KEYPAD_DIMS[0])])
    for c in range(Interface.KEYPAD_DIMS[1])
]


class VirtualImplementation:
    def __init__(self):
        self.keypad_button_objs = [
            [
                sg.Button(keypad_buttons[i][j], size=(max_by_col[j] + 1, 1))
                for j in range(Interface.KEYPAD_DIMS[1])
            ]
            for i in range(Interface.KEYPAD_DIMS[0])
        ]
        self.lcd_chars = [
            [
                sg.Text(
                    " ", background_color="blue", size=(2, 1), justification="center"
                )
                for j in range(Interface.DISPLAY_DIMS[1])
            ]
            for i in range(Interface.DISPLAY_DIMS[0])
        ]

        self.layout = [
            [sg.Column(self.lcd_chars, justification="c")],
            [sg.Column(self.keypad_button_objs, justification="c")],
        ]

        self.window = sg.Window(
            "Plate Calculator Simulator", self.layout, finalize=True, size=(500, 400)
        )

    def write_text(self, text, i, j):
        for dx in range(len(text)):
            self.lcd_chars[i][j + dx].update(value=text[dx])

    def read_key(self):
        event, values = self.window.read()

        for k, v in Key.LABELS.items():
            if v == event:
                return k

        return None

    def get_time(self):
        return int(time())

    def display_on(self):
        self.set_display(" ", "blue")

    def display_off(self):
        self.set_display(" ", "black")

    def clear_display(self):
        self.set_display(" ")

    def set_display(self, value, bg_color=None):
        for row in self.lcd_chars:
            for char in row:
                if bg_color:
                    char.update(value=value, background_color=bg_color)
                else:
                    char.update(value=value, background_color=bg_color)
