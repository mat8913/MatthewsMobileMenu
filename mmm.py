#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# Matthew's Mobile Menu
# Copyright (C) 2022 by Matthew Harm Bekkema <id@mbekkema.name>

import fcntl
import termios
from pathlib import Path
from typing import Iterator, Optional, Protocol

MENU_FILE_NAME = '.mmm-menufile'


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


def get_self_and_parent_paths(path: Path) -> Iterator[Path]:
    yield path
    for parent in path.parents:
        yield parent


def get_menu_file_path() -> Path:
    for p in get_self_and_parent_paths(Path.cwd()):
        menu_file_path = p / MENU_FILE_NAME
        if menu_file_path.is_file():
            return menu_file_path
    raise Exception('No menu file found in working directory or any parent directories: ' + MENU_FILE_NAME)


def load_menu_file(menu_file_path: Path) -> Menu:
    with open(menu_file_path) as f:
        menu_items: list[MenuItem] = [TerminalMenuItem(line.rstrip()) for line in f]
    return Menu(menu_items)


def main() -> None:
    menu_file_path = get_menu_file_path()
    menu = load_menu_file(menu_file_path)
    selected_menu_item = menu.ask_and_get_selected_item()
    selected_menu_item.do_action()


if __name__ == '__main__':
    main()
