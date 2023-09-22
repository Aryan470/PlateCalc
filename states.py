import calculations
from interfaces.interface import Key, Interface
from interfaces.characters import CustomCharacters


class State:
    def __init__(self, interface):
        self.interface = interface

    def process_input(self, key):
        raise NotImplementedError()

    def power_off(self):
        return SleepState(self.interface)

    def render(self):
        raise NotImplementedError()


class SleepState(State):
    def __init__(self, interface):
        super().__init__(interface)
        interface.display_off()
        interface.set_sleep()

    def render(self):
        raise NotImplementedError()


class PromptState(State):
    UNIT_STATES = (("LB", "LB"), ("LB", "KG"), ("KG", "KG"), ("KG", "LB"))

    def __init__(self, interface):
        super().__init__(interface)
        self.curr_val = 0
        self.num_digits = 0
        self.percent = 100
        self.percent_num_digits = 3
        self.unit_state = interface.config_read("prompt")["unit_state"]
        self.pos = "weight"

    def format_first_row(weight, unit_state):
        return "Weight: %-4d(%s)" % (weight, PromptState.UNIT_STATES[unit_state][0])

    def format_second_row(percent, unit_state):
        percent_str = "%d%%" % percent
        unit_str = "%s plates" % PromptState.UNIT_STATES[unit_state][1]
        num_cols = Interface.DISPLAY_DIMS[1]

        total_spaces = num_cols - len(percent_str) - len(unit_str) - 1
        right_spaces = total_spaces // 2
        left_spaces = total_spaces - right_spaces

        return percent_str + " " * left_spaces + "|" + " " * right_spaces + unit_str

    def render(self):
        self.interface.clear_display()

        first_row = PromptState.format_first_row(self.curr_val, self.unit_state)
        second_row = PromptState.format_second_row(self.percent, self.unit_state)

        self.interface.write_text(first_row, 0, 0)
        self.interface.write_text(second_row, 1, 0)

        if self.pos == "weight":
            self.interface.blink_cursor_at(0, len("Weight: ") + self.num_digits)
        elif self.pos == "percent":
            self.interface.blink_cursor_at(1, self.percent_num_digits)

    def toggle_pos(self):
        if self.pos == "percent":
            if self.percent == 0:
                self.percent = 100
                self.percent_num_digits = 3
            self.pos = "weight"
        else:
            self.pos = "percent"
            self.percent = 0
            self.percent_num_digits = 0

    def get_results(self):
        self.interface.cursor_off()
        return ResultState(
            self.interface,
            self.curr_val,
            self.percent,
            self.UNIT_STATES[self.unit_state],
        )

    def process_input(self, key):
        if key == Key.TIMEOUT or key == Key.POWER:
            return self.power_off()

        if not Key.is_numeric(key):
            if key == Key.CLEAR:
                self.curr_val = 0
                self.num_digits = 0
            elif key == Key.ENTER:
                if self.pos == "percent":
                    self.toggle_pos()
                else:
                    return self.get_results()
            elif key == Key.UNIT:
                self.unit_state += 1
                self.unit_state %= len(self.UNIT_STATES)
                curr_prompt_config = self.interface.config_read("prompt")
                curr_prompt_config["unit_state"] = self.unit_state
                self.interface.config_write("prompt", curr_prompt_config)
            elif key == Key.PERCENT:
                self.toggle_pos()
            elif key == Key.CONFIG:
                return MenuState(self.interface)
        else:
            if self.pos == "weight":
                if self.num_digits == 3:
                    return self.get_results()
                else:
                    # otherwise add this digit to the end
                    self.curr_val *= 10
                    self.curr_val += key
                    self.num_digits += 1

                    if self.curr_val == 0:
                        self.num_digits = 0
            elif self.pos == "percent":
                if self.percent_num_digits == 3:
                    self.toggle_pos()
                else:
                    self.percent *= 10
                    self.percent += key
                    self.percent_num_digits += 1

                    if self.percent == 0:
                        self.percent_num_digits = 0

        return self


class MenuAction:
    def __init__(self, title):
        self.title = title

    def action(self, interface):
        raise NotImplementedError()

    def get_title(self, interface):
        return self.title


class EditPlateAction(MenuAction):
    def __init__(self, unit, val):
        super().__init__(val)
        self.unit = unit

    def get_title(self, interface):
        result = self.title
        if interface.config_read("weights")[self.unit]["plates"][self.title]["using"]:
            result += " *"
        return result

    def action(self, interface):
        curr_weight_config = interface.config_read("weights")
        curr_using = curr_weight_config[self.unit]["plates"][self.title]["using"]
        curr_weight_config[self.unit]["plates"][self.title]["using"] = not curr_using
        interface.config_write("weights", curr_weight_config)


# TODO: refactor to use EditRadioAction(unit, weight_type, val)
class EditCollarAction(MenuAction):
    def __init__(self, unit, val):
        super().__init__(val)
        self.unit = unit

    def get_title(self, interface):
        result = self.title
        if interface.config_read("weights")[self.unit]["collars"][self.title]["using"]:
            result += " *"
        return result

    def action(self, interface):
        curr_weight_config = interface.config_read("weights")
        num_collars = len(curr_weight_config[self.unit]["collars"])
        if num_collars < 2:
            return

        for collar in curr_weight_config[self.unit]["collars"]:
            curr_weight_config[self.unit]["collars"][collar]["using"] = False

        curr_weight_config[self.unit]["collars"][self.title]["using"] = True
        curr_weight_config[self.unit]["collar"] = curr_weight_config[self.unit][
            "collars"
        ][self.title]["value"]
        interface.config_write("weights", curr_weight_config)


class EditBarAction(MenuAction):
    def __init__(self, unit, val):
        super().__init__(val)
        self.unit = unit

    def get_title(self, interface):
        result = self.title
        if interface.config_read("weights")[self.unit]["bars"][self.title]["using"]:
            result += " *"
        return result

    def action(self, interface):
        curr_weight_config = interface.config_read("weights")
        num_bars = len(curr_weight_config[self.unit]["bars"])
        if num_bars < 2:
            return

        for bar in curr_weight_config[self.unit]["bars"]:
            curr_weight_config[self.unit]["bars"][bar]["using"] = False

        curr_weight_config[self.unit]["bars"][self.title]["using"] = True
        curr_weight_config[self.unit]["bar"] = curr_weight_config[self.unit]["bars"][
            self.title
        ]["value"]
        interface.config_write("weights", curr_weight_config)


class Menu:
    def __init__(self, title, parent=None, action=None, create_exit=True):
        self.title = title
        self.parent = parent
        self.row = 0

        self.submenus = []
        if create_exit:
            self.add_submenu(Menu("Back", create_exit=False))

    def add_submenu(self, child):
        child.parent = self
        self.submenus.append(child)

    def get_title(self, interface):
        return self.title

    def scroll_down(self):
        if self.row < len(self.submenus) - 2:
            self.row += 1

    def scroll_up(self):
        if self.row > 0:
            self.row -= 1

    def navigate(self, key, interface):
        if key == Key.ONE:
            if self.row == 0:
                if self.parent is None:
                    return PromptState(interface)
                return self.parent

            if isinstance(self.submenus[self.row], MenuAction):
                self.submenus[self.row].action(interface)
                return self
            return self.submenus[self.row]
        elif key == Key.TWO and self.row + 1 < len(self.submenus):
            if isinstance(self.submenus[self.row + 1], MenuAction):
                self.submenus[self.row + 1].action(interface)
                return self
            return self.submenus[self.row + 1]
        elif key == Key.EIGHT:
            self.scroll_up()
        elif key == Key.NINE:
            self.scroll_down()

        return self

    def render(self, interface):
        first_row = "1: %s" % (self.submenus[self.row].get_title(interface))
        if self.row > 0:
            first_row += " " * (Interface.DISPLAY_DIMS[1] - len(first_row) - 1)
            first_row += chr(CustomCharacters.SCROLL_UP_LABEL["index"])

        second_row = ""
        if self.row + 1 < len(self.submenus):
            second_row = "2: %s" % (self.submenus[self.row + 1].get_title(interface))
            if self.row + 2 < len(self.submenus):
                second_row += " " * (Interface.DISPLAY_DIMS[1] - len(second_row) - 1)
                second_row += chr(CustomCharacters.SCROLL_DOWN_LABEL["index"])
        return [first_row, second_row]

    def menu_init(interface):
        Menu.HOME = Menu("Home")
        plate_menu = Menu("Edit plates")
        bar_menu = Menu("Edit bars")
        collar_menu = Menu("Edit collars")
        Menu.HOME.add_submenu(plate_menu)
        Menu.HOME.add_submenu(bar_menu)
        Menu.HOME.add_submenu(collar_menu)

        for unit in sorted(interface.config_read("weights").keys()):
            bar_unit_menu = Menu(unit)
            plate_unit_menu = Menu(unit)
            collar_unit_menu = Menu(unit)

            plate_menu.add_submenu(plate_unit_menu)
            bar_menu.add_submenu(bar_unit_menu)
            collar_menu.add_submenu(collar_unit_menu)


            for plate in sorted(
                interface.config_read("weights")[unit]["plates"].keys(),
                key=lambda x: float(x),
                reverse=True,
            ):
                plate_action = EditPlateAction(unit, plate)
                plate_unit_menu.add_submenu(plate_action)

            for bar in sorted(
                interface.config_read("weights")[unit]["bars"].keys(),
                key=lambda x: float(x),
                reverse=True,
            ):
                bar_action = EditBarAction(unit, bar)
                bar_unit_menu.add_submenu(bar_action)

            for collar in sorted(
                interface.config_read("weights")[unit]["collars"].keys(),
                key=lambda x: float(x),
                reverse=True,
            ):
                collar_action = EditCollarAction(unit, collar)
                collar_unit_menu.add_submenu(collar_action)


class MenuState(State):
    def __init__(self, interface):
        super().__init__(interface)
        self.curr_menu = Menu.HOME

    def process_input(self, key):
        if key == Key.TIMEOUT or key == Key.POWER:
            return SleepState(self.interface)
        elif key == Key.CONFIG:
            return PromptState(self.interface)
        elif Key.is_numeric(key):
            self.curr_menu = self.curr_menu.navigate(key, self.interface)
            if not isinstance(self.curr_menu, Menu):
                return self.curr_menu
        return self

    def render(self):
        self.interface.clear_display()
        rows = self.curr_menu.render(self.interface)
        self.interface.write_text(rows[0], 0, 0)
        self.interface.write_text(rows[1], 1, 0)


class ResultState(State):
    def __init__(self, interface, weight, percent, units):
        super().__init__(interface)
        weight = round(weight * percent / 100)

        plate_counts, end_weight = calculations.get_plate_counts(
            weight, units, interface
        )

        self.display_strings = calculations.get_plate_count_strings(plate_counts)
        bar_val = interface.config_read("weights")[units[1]]["bar"]
        bar_str = "%d bar" % (bar_val)
        self.display_strings.insert(0, bar_str)
        if end_weight > bar_val * 100:
            self.display_strings.insert(1, "+")

        collar_val = interface.config_read("weights")[units[1]]["collar"]
        if collar_val > 0 and end_weight > bar_val * 100:
            collar_str = "%s collars" % calculations.format_hundredths_weight(collar_val)
            self.display_strings.append(collar_str)

        self.units = units
        self.scroll_level = 0

        self.aux_weight = None
        if self.units[0] != self.units[1]:
            if self.units[1] == "KG":
                self.aux_weight = round(calculations.kg_to_lb(end_weight) / 100)
            else:
                self.aux_weight = round(calculations.lb_to_kg(end_weight) / 100)
        self.weight = calculations.format_hundredths_weight(end_weight)
        self.make_rows()

    def make_rows(self):
        if self.aux_weight is not None:
            self.rows = [
                "%s%s/%d%s:"
                % (self.weight, self.units[1], self.aux_weight, self.units[0])
            ]
        else:
            self.rows = ["%s%s:" % (self.weight, self.units[1])]

        for display_string in self.display_strings:
            # if we can fit this in the current row
            if (
                self.rows[-1] == ""
                or len(self.rows[-1]) + 1 + len(display_string)
                <= Interface.DISPLAY_DIMS[1] - 1
            ):
                if not self.rows[-1]:
                    self.rows[-1] = display_string
                else:
                    self.rows[-1] += " " + display_string
            else:
                # we cannot fit it in this row, add a new one
                self.rows.append(display_string)

        if len(self.display_strings) == 0:
            self.rows.append("(no plates)")

    def process_input(self, key):
        if key == Key.TIMEOUT or key == Key.POWER:
            return self.power_off()

        if key == 8:
            self.scroll_up()
            return self
        if key == 9:
            self.scroll_down()
            return self

        return PromptState(self.interface)

    def scroll_down(self):
        if self.scroll_level < len(self.rows) - 2:
            self.scroll_level += 1

    def scroll_up(self):
        if self.scroll_level > 0:
            self.scroll_level -= 1

    def render(self):
        self.interface.clear_display()

        if self.scroll_level < len(self.rows):
            self.interface.write_text(self.rows[self.scroll_level], 0, 0)

            # if we can scroll up, show the scroll button
            if self.scroll_level > 0:
                self.interface.write_text(
                    chr(CustomCharacters.SCROLL_UP_LABEL["index"]),
                    0,
                    Interface.DISPLAY_DIMS[1] - 1,
                )

            # display next row
            if self.scroll_level + 1 < len(self.rows):
                self.interface.write_text(self.rows[self.scroll_level + 1], 1, 0)

            # if we can scroll down, show scroll button
            if self.scroll_level + 2 < len(self.rows):
                self.interface.write_text(
                    chr(CustomCharacters.SCROLL_DOWN_LABEL["index"]),
                    1,
                    Interface.DISPLAY_DIMS[1] - 1,
                )
