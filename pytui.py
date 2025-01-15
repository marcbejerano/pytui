#!/usr/bin/env python3

from typing import Callable, Self

import curses
import os

#--
# Default styles
#--
Style = {
    'TITLE':                    curses.A_BOLD,
    'BUTTON_FOCUS':             curses.A_REVERSE,
    'BUTTON_UNFOCUS':           curses.A_NORMAL,
    'CHECKBOX_FOCUS':           curses.A_BOLD,
    'CHECKBOX_UNFOCUS':         curses.A_NORMAL,
    'CHECKBOX_CHECKED':         '\u2713',
    'CHECKBOX_UNCHECKED':       ' ',
    'TEXT':                     curses.A_NORMAL,
    'INPUT_FOCUS':              curses.A_REVERSE,
    'INPUT_UNFOCUS':            curses.A_NORMAL,
}

#---
# Component
#
# Description:
#   Basic component than can have focus and can contain other Components
#---
class Component:
    def __init__(self):
        self.children = []
        self.focused_child = None
        self.has_focus = False
        self.can_focus = False
        self.focusable_count = 0

    def get_focus(self):
        if self.can_focus:
            self.has_focus = True

    def lose_focus(self):
        if self.can_focus:
            self.has_focus = False

    def key_pressed(self, key):
        pass
    
    def add_child(self, child: Self):
        self.children.append(child)
        if child.can_focus:
            self.focusable_count = self.focusable_count + 1

    def current_child(self) -> Self:
        if len(self.children) > 0:
            return self.children[self.focused_child]
        else:
            return None
    
    def first_child(self) -> Self:
        if len(self.children) > 0:
            self.focused_child = 0
            while self.focused_child < len(self.children):
                if self.children[self.focused_child].can_focus:
                    return self.children[self.focused_child]
                self.focused_child = self.focused_child + 1
            return None
        else:
            return None

    def last_child(self) -> Self:
        if len(self.children) > 0:
            self.focused_child = len(self.children) - 1
            while self.focused_child > 0:
                if self.children[self.focused_child].can_focus:
                    return self.children[self.focused_child]
                self.focused_child = self.focused_child - 1
            return None
        else:
            return None
    
    def next_child(self) -> Self:
        if len(self.children) > 0:
            if self.focused_child == len(self.children) - 1:
                self.focused_child = 0
                return self.first_child()
            else:
                while self.focused_child < len(self.children):
                    self.focused_child = self.focused_child + 1
                    if self.children[self.focused_child].can_focus:
                        return self.children[self.focused_child]
                return None
        else:
            return None

    def previous_child(self) -> Self:
        if len(self.children) > 0:
            if self.focused_child == 0:
                self.focused_child = len(self.children) - 1
                return self.last_child()
            else:
                while self.focused_child > 0:
                    self.focused_child = self.focused_child - 1
                    if self.children[self.focused_child].can_focus:
                        return self.children[self.focused_child]
                return None
        else:
            return None

#---
# VisualComponent
#
# Description:
#   Basic visual component that maintains location and an idx
#---
class VisualComponent(Component):
    def __init__(self, win: any, row: int, column: int, idx: int, can_focus: bool = False):
        Component.__init__(self)
        self.win = win
        self.row = row
        self.column = column
        self.idx = idx
        self.can_focus = can_focus
        self.cursor_offset = 0

    def getyx(self) -> (int, int):
        return self.row, self.column

    def repaint(self):
        pass

    def get_focus(self):
        Component.get_focus(self)
        self.repaint()

    def lose_focus(self):
        Component.lose_focus(self)
        self.repaint()

#---
# FrameWindow
#---
class FrameWindow(VisualComponent):
    def __init__(self, stdscr: any, title: str = None):
        VisualComponent.__init__(self, stdscr, 0, 0, 0)
        self.rows, self.columns = self.win.getmaxyx()
        self.title = title
        self.resize()
        curses.noecho()
        curses.curs_set(0)

    def __del__(self):
        curses.curs_set(1)

    def resize(self):
        self.rows, self.columns = self.win.getmaxyx()
        self.repaint()

    def repaint(self):
        self.win.clear()
        self.win.border()
        if self.title is not None:
            column = int((self.columns - len(self.title) + 2) / 2)
            self.win.addstr(0, column, f" {self.title} ", Style['TITLE'])

        for child in self.children:
            child.repaint()

        self.win.refresh()

    def process(self):
        self.repaint()

        curses.curs_set(0)
        curses.noecho()

        if self.first_child() is not None:
            self.current_child().get_focus()

            self.win.nodelay(True)
            self.win.keypad(True)
            key = None

            while key != chr(27):

                if key == chr(9): # KEY_TAB
                    self.current_child().lose_focus()
                    if self.next_child() is not None:
                        self.current_child().get_focus()
                elif key == "KEY_BTAB":
                    self.current_child().lose_focus()
                    if self.previous_child() is not None:
                        self.current_child().get_focus()
                elif key is not None:
                    self.current_child().key_pressed(key)

                try:
                    row, column = self.current_child().getyx()
                    key = self.win.getkey(row, column + self.current_child().cursor_offset)
                except Exception:
                    key = None


#---
# Button
#
# Description:
#   Basic button visual component
#---
class Button(VisualComponent):
    def __init__(self, win: any, row: int, column: int, idx: int, label: str, width: int = 0, call_fn: Callable = None):
        VisualComponent.__init__(self, win, row, column, idx, can_focus=True)
        self.label = label
        self.width = width
        self.call_fn = call_fn
        self.cursor_offset = (int(width / 2)) if width > 0 else (int(len(label) /2))

    def repaint(self):
        text_label = self.label if self.width == 0 else f"{self.label:^{self.width}}"
        if self.has_focus:
            self.win.addstr(self.row, self.column, text_label, Style['BUTTON_FOCUS'])
        else:
            self.win.addstr(self.row, self.column, text_label, Style['BUTTON_UNFOCUS'])

    def key_pressed(self, key: str):
        if (key == os.linesep or key == " ") and self.call_fn is not None:
            self.call_fn(self)
            
#---
# Checkbox
#
# Description:
#   Basic visual state component
#---
class Checkbox(VisualComponent):
    def __init__(self, win: any, row: int, column: int, idx: int, label: str, width: int = 0, state: bool = False, call_fn: Callable = None):
        VisualComponent.__init__(self, win, row, column, idx, can_focus=True)
        self.label = label
        self.width = width
        self.state = state
        self.call_fn = call_fn
        self.cursor_offset = 1

    def get_focus(self):
        VisualComponent.get_focus(self)
        curses.curs_set(1)

    def lose_focus(self):
        VisualComponent.lose_focus(self)
        curses.curs_set(0)

    def repaint(self):
        text_label = self.label if self.width == 0 else f"{self.label:{self.width}}"
        attrib = Style['CHECKBOX_FOCUS'] if self.has_focus else Style['CHECKBOX_UNFOCUS']
        checkmark = Style['CHECKBOX_CHECKED'] if self.state else Style['CHECKBOX_UNCHECKED']
        self.win.addstr(self.row, self.column, f"[{checkmark}] {text_label}", attrib)

    def key_pressed(self, key):
        if key == os.linesep or key == ' ':
            self.state = not self.state
            self.repaint()
            if self.call_fn is not None:
                self.call_fn(self)

#---
# Text
#
# Description:
#   Basic text component used to retain text state during a repaint
#---
class Text(VisualComponent):
    def __init__(self, win: any, row: int, column: int, idx: int, text: str, width: int = 0, attrib: any = None):
        VisualComponent.__init__(self, win, row, column, idx, can_focus=False)
        self.width = width
        self.text = text
        self.attrib = attrib

    def repaint(self):
        text = self.text if self.width == 0 else f"{self.text:{self.width}}"
        attrib = self.attrib if self.attrib is not None else Style['TEXT']
        self.win.addstr(self.row, self.column, text, attrib)

#---
# Input
#
# Description:
#   Basic line input component that supports Insert, Delete, Backspace, Left, Right, Home, and End keys
#---
class Input(VisualComponent):
    def __init__(self, win: any, row: int, column: int, idx: int, width: int = 0, value: str = '', max_width: int = 0, validate_fn: Callable = None):
        VisualComponent.__init__(self, win, row, column, idx, can_focus=True)
        self.width = width
        self.value = value
        self.max_width = max_width
        self.validate_fn = validate_fn
        self.insert_mode = True
        self.cursor_offset = len(value)

    def get_focus(self):
        VisualComponent.get_focus(self)
        curses.curs_set(1)

    def lose_focus(self):
        VisualComponent.lose_focus(self)
        curses.curs_set(0)

    def repaint(self):
        text_label = f"{self.value:<{self.width}}"
        attrib = Style['INPUT_FOCUS'] if self.has_focus else Style['INPUT_UNFOCUS']
        self.win.addstr(self.row, self.column, text_label, attrib)

    def key_pressed(self, key):
        validx = True if self.validate_fn is None else self.validate_fn(self.value)

        if validx:
            if key == 'KEY_LEFT' and self.cursor_offset > 0:
                self.cursor_offset = self.cursor_offset - 1
            elif key == 'KEY_RIGHT' and self.cursor_offset < len(self.value):
                self.cursor_offset = self.cursor_offset + 1
            elif key == 'KEY_HOME':
                self.cursor_offset = 0
            elif key == 'KEY_END':
                self.cursor_offset = len(self.value)
            elif key == 'KEY_IC': # Insert toggle
                self.insert_mode = not self.insert_mode
                curses.curs_set(2 if self.insert_mode else 1)
            elif key == 'KEY_DC' and len(self.value) > 0:
                left_text = self.value[:self.cursor_offset]
                right_text = self.value[self.cursor_offset + 1:]
                self.value = left_text + right_text
                self.repaint()
            elif key == 'KEY_BACKSPACE' and self.cursor_offset > 0:
                left_text = self.value[:self.cursor_offset - 1]
                right_text = self.value[self.cursor_offset:]
                self.value = left_text + right_text
                self.cursor_offset = self.cursor_offset - 1
                self.repaint()
            elif len(key) == 1 and ord(key) >= 32:
                if self.insert_mode and len(self.value) < self.max_width:
                    left_text = self.value[:self.cursor_offset]
                    right_text = self.value[self.cursor_offset:]
                    self.value = left_text + key + right_text
                    self.cursor_offset = self.cursor_offset + 1
                else:
                    left_text = self.value[:self.cursor_offset]
                    right_text = self.value[self.cursor_offset + 1:]
                    if self.cursor_offset == len(self.value) and self.cursor_offset < self.max_width:
                        self.cursor_offset = self.cursor_offset + 1
                    self.value = left_text + key + right_text
                self.repaint()


