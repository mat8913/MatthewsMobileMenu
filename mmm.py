#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# Matthew's Mobile Menu
# Copyright (C) 2022 by Matthew Harm Bekkema <id@mbekkema.name>

import fcntl
import termios
from pathlib import Path
from typing import Iterator

MENU_FILE_NAME = '.mmm-menufile'


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


def load_menu_file(menu_file_path: Path) -> list[str]:
    with open(menu_file_path) as f:
        return [line.rstrip() for line in f]


def simulate_terminal_input(input: str) -> None:
    binput = input.encode('utf-8')
    for i in range(len(binput)):
        b = binput[i:i+1]
        fcntl.ioctl(0, termios.TIOCSTI, b)
    if not input.endswith('\n'):
        print()


def print_menu(menu: list[str]) -> None:
    i = 0
    for item in menu:
        print(str(i) + ')\t' + item)
        i = i + 1


def parse_selection(menu: list[str], input: str) -> str:
    return menu[int(input)]


def main() -> None:
    menu_file_path = get_menu_file_path()
    menu = load_menu_file(menu_file_path)
    print_menu(menu)
    user_input = input('> ')
    selected_command = parse_selection(menu, user_input)
    simulate_terminal_input(selected_command + '\n')


if __name__ == '__main__':
    main()
