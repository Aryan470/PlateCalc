from interfaces.interface import Interface
from interfaces.hardware.hardware_interface import HardwareImplementation
import states
from machine import Pin

interface = Interface(
    HardwareImplementation(
        [Pin(i, Pin.OUT) for i in range(3, -1, -1)],
        [Pin(i, Pin.OUT) for i in range(4, 8)],
        {
            "BL": Pin(22, Pin.OUT),
            "RS": Pin(21, Pin.OUT),
            "EN": Pin(20, Pin.OUT),
            "D4": Pin(19, Pin.OUT),
            "D5": Pin(18, Pin.OUT),
            "D6": Pin(17, Pin.OUT),
            "D7": Pin(16, Pin.OUT),
        },
    )
)
states.Menu.menu_init(interface)

curr_state = states.PromptState(interface)

while True:
    curr_state.render()
    key = interface.read_key()
    curr_state = curr_state.process_input(key)
