#!/usr/bin/env python3

from curses import wrapper

import curses
import os
import pytui
import subprocess

def click_button(source: pytui.Button):
    source.win.addstr(1, 1, f"Clicked on button with id={source.id}      ")

def click_checkbox(source: pytui.Checkbox):
    checkmark = pytui.Style['CHECKBOX_CHECKED'] if source.state else pytui.Style['CHECKBOX_UNCHECKED']
    source.win.addstr(1, 1, f"Clicked on checkbox id={source.id}, state={checkmark}")

def main(stdscr: any):
    frame = pytui.FrameWindow(stdscr, title="This is a Test")
    frame.add_child(pytui.Button    (stdscr, row=2, column=2, width=20, id=12345, label="Button", call_fn=click_button))
    frame.add_child(pytui.Button    (stdscr, row=4, column=2, width=20, id=54321, label="Next", call_fn=click_button))
    frame.add_child(pytui.Checkbox  (stdscr, row=6, column=2, width=20, id=13579, label="Checkbox", call_fn=click_checkbox))
    frame.add_child(pytui.Text      (stdscr, row=8, column=2, width=30, id=13579, text="plain text", attrib=curses.A_BOLD))
    frame.add_child(pytui.Input     (stdscr, row=10, column=2, width=30, id=13579, value="edit this line of text", max_width=60))
    frame.process()

if __name__ == "__main__":
    os.environ.setdefault('ESCDELAY', '25')
    wrapper(main)
    subprocess.run(['stty', 'sane'])
