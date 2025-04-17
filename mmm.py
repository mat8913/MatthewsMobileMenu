#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# Matthew's Mobile Menu
# Copyright (C) 2022 by Matthew Harm Bekkema <id@mbekkema.name>

import fcntl
import termios
from pathlib import Path
from typing import Iterator, Optional, Protocol


class MenuItem(Protocol):
    def get_name(self) -> str: ...
    def do_action(self) -> None: ...


class Menu():
    menu_items: list[MenuItem]

    def __init__(self, menu_items: list[MenuItem]) -> None:
        self.menu_items = menu_items

    def ask_and_get_selected_item(self) -> MenuItem:
        self.print_menu()
        user_input = input('> ')
        selected_menu_item = self.parse_selection(user_input)
        return selected_menu_item

    def parse_selection(self, input: str) -> MenuItem:
        return self.menu_items[int(input)]

    def print_menu(self) -> None:
        for i, menu_item in enumerate(self.menu_items):
            print(f"{i})\t{menu_item.get_name()}")


class MmmState():
    menu_stack: list[Menu]

    def __init__(self) -> None:
        self.menu_stack = []

    def pop_menu(self) -> None:
        self.menu_stack.pop()

    def push_menu(self, menu: Menu) -> None:
        self.menu_stack.append(menu)

    def get_menu(self) -> Optional[Menu]:
        try:
            return self.menu_stack[-1]
        except IndexError:
            return None

    def menu_stack_length(self) -> int:
        return len(self.menu_stack)


class BackMenuItem():
    def __init__(self, state: MmmState):
        self.state = state

    def get_name(self) -> str:
        if self.state.menu_stack_length() <= 1:
            return "(Quit)"
        else:
            return "(Go Back)"

    def do_action(self) -> None:
        self.state.pop_menu()


class TerminalMenuItem():
    name: str
    cmd: str

    def __init__(self, name: str, cmd: Optional[str] = None) -> None:
        self.name = name
        self.cmd = cmd if cmd is not None else name

    def get_name(self) -> str:
        return self.name

    def do_action(self) -> None:
        self.simulate_terminal_input(self.cmd + '\n')
        quit()

    def simulate_terminal_input(self, input: str) -> None:
        binput = input.encode('utf-8')
        for i in range(len(binput)):
            b = binput[i:i+1]
            fcntl.ioctl(0, termios.TIOCSTI, b)
        if not input.endswith('\n'):
            print()


class CustomMenuLoader():
    MENU_FILE_NAME = '.mmm-menufile'

    def load_custom_menu(self) -> list[MenuItem]:
        menu_file_path = self.get_menu_file_path()
        if menu_file_path is not None:
            return self.load_menu_file(menu_file_path)
        else:
            return []

    def load_menu_file(self, menu_file_path: Path) -> list[MenuItem]:
        with open(menu_file_path) as f:
            return [TerminalMenuItem(line.rstrip()) for line in f]

    def get_menu_file_path(self) -> Optional[Path]:
        for p in self.get_self_and_parent_paths(Path.cwd()):
            menu_file_path = p / CustomMenuLoader.MENU_FILE_NAME
            if menu_file_path.is_file():
                return menu_file_path
        return None

    def get_self_and_parent_paths(self, path: Path) -> Iterator[Path]:
        yield path
        for parent in path.parents:
            yield parent


class InitialMenuBuilder():
    def build_initial_menu(self, state: MmmState) -> Menu:
        back_items = [BackMenuItem(state)]
        custom_menu_items = CustomMenuLoader().load_custom_menu()

        return Menu(back_items + custom_menu_items)


class MmmApplication():
    def run(self) -> None:
        state = MmmState()
        initial_menu = InitialMenuBuilder().build_initial_menu(state)
        state.push_menu(initial_menu)

        while True:
            menu = state.get_menu()
            if not menu:
                break
            selected_menu_item = menu.ask_and_get_selected_item()
            selected_menu_item.do_action()


if __name__ == '__main__':
    MmmApplication().run()
