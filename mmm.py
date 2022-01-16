#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# Matthew's Mobile Menu
# Copyright (C) 2022 by Matthew Harm Bekkema <id@mbekkema.name>

import fcntl
import termios
from pathlib import Path


MENU_FILE_NAME='.mmm-menufile'


def get_self_and_parent_paths(path):
    yield path
    for parent in path.parents:
        yield parent


def get_menu_file_path():
    for p in get_self_and_parent_paths(Path.cwd()):
        menu_file_path = p / MENU_FILE_NAME
        if menu_file_path.is_file():
            return menu_file_path
    raise Exception('No menu file found in working directory or any parent directories: ' + MENU_FILE_NAME)


def load_menu_file(menu_file_path):
    with open(menu_file_path) as f:
        return [l.rstrip() for l in f]


def simulate_terminal_input(input):
    for c in input:
        fcntl.ioctl(0, termios.TIOCSTI, c)
    if not input.endswith('\n'):
        print()


def print_menu(menu):
    i = 0
    for item in menu:
        print(str(i) + ')\t' + item)
        i = i + 1


def parse_selection(menu, input):
    return menu[int(input)]


def main():
    menu_file_path = get_menu_file_path()
    menu = load_menu_file(menu_file_path)
    print_menu(menu)
    user_input = input('> ')
    selected_command = parse_selection(menu, user_input)
    simulate_terminal_input(selected_command + '\n')


if __name__ == '__main__':
    main()
