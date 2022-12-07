from __future__ import annotations

from .gui_helper import GUI_Helper
from .functions import hex_0fill

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

class Decoded_Value_Display(GUI_Helper):
    _parent: GUI_Helper
    def __init__(self, parent: GUI_Helper, value_name: str, display_var: tk.StringVar, metadata, tooltip_width=250):
        super().__init__(parent, None, parent._logger)

        self._name = value_name
        #self._metadata = metadata
        self._bits = metadata["bits"]
        self._info = metadata["info"]
        self._enabled = False
        self._display_var = display_var
        self._tooltip_width = tooltip_width

        show_binary = metadata["show_binary"]
        if show_binary == "Inline" or show_binary == True:
            self._inline = True
            self._show_binary = True
        elif show_binary == "New Line":
            self._inline = False
            self._show_binary = True
        else:
            self._inline = True
            self._show_binary = False

    def enable(self):
        self._enabled = True
        if hasattr(self, "_value_entry"):
            self._value_entry.config(state="normal")

    def disable(self):
        self._enabled = False
        if hasattr(self, "_value_entry"):
            self._value_entry.config(state="disabled")

    def set_position(self, col: int, row: int):
        self._frame.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S), padx=5, pady=5)

    def get_required_size(self):
        return (self._frame.winfo_reqwidth(), self._frame.winfo_reqheight())

    def get_size(self):
        return (self._frame.winfo_width(), self._frame.winfo_height())

    def prepare_display(self, element: tk.Tk, col: int, row: int):
        self._frame = ttk.LabelFrame(element, text=self._name)
        self.set_position(col, row)

        state = 'disabled'
        if self._enabled:
            state = 'normal'

        if self._bits == 1:
            self._value_entry = ttk.Checkbutton(self._frame, variable=self._display_var, state=state, onvalue="1", offvalue="0")
            self._value_entry.grid(column=100, row=100, sticky=tk.W)
            self._display_var.trace('w', self._update_checkbutton_text)
            self._update_checkbutton_text()
        else:
            self._value_label = ttk.Label(self._frame, text="Value:")
            self._value_label.grid(column=100, row=100, sticky=tk.E)

            from math import ceil
            self._value_entry = ttk.Entry(self._frame, textvariable=self._display_var, state=state, width=max(5, ceil(self._bits/4) + 2))
            self._value_entry.grid(column=200, row=100, sticky=tk.W)

            from .functions import validate_variable_bit_register
            self._register_validate_cmd = (self._frame.register(lambda string, bits=self._bits: validate_variable_bit_register(string, bits)), '%P')
            self._register_invalid_cmd  = (self._frame.register(self.invalid_register_value), '%P')
            self._value_entry.config(validate='key', validatecommand=self._register_validate_cmd, invalidcommand=self._register_invalid_cmd)

            if self._show_binary:
                binary_row = 200
                binary_col = 100
                padding = 0
                if self._inline:
                    binary_row = 100
                    binary_col = 300
                    padding = 5

                self._value_binary_label = ttk.Label(self._frame, text="Binary:", padding=padding)
                self._value_binary_label.grid(column=binary_col, row=binary_row, sticky=tk.E)

                self._value_binary_frame = ttk.Frame(self._frame)
                self._value_binary_frame.grid(column=binary_col+100, row=binary_row, sticky=(tk.W, tk.S, tk.N), padx=0, pady=0)
                self._frame.rowconfigure(binary_row, weight=1)
                self._value_binary_frame.rowconfigure(100, weight=1)

                self._value_binary_prefix = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0b")
                self._value_binary_prefix.grid(column=100, row=100)

                for idx in range(self._bits):
                    bit = self._bits - 1 - idx
                    bit_label = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
                    bit_label.grid(column = 200 + 100*idx, row = 100)
                    bit_label.bind("<Button-1>", lambda e, bit=bit:self._toggle_bit(bit))
                    self.__setattr__("_value_binary_bit{}".format(bit), bit_label)

                self._display_var.trace('w', self._update_binary_repr)
                self._update_binary_repr()

        if self._info != "":
            self._info_button = ttk.Label(self._frame, text="ⓘ", borderwidth=1, relief="solid", padding=2)
            self._frame.columnconfigure(499, weight=1)
            self._info_button.grid(column=500, row=100)
            self._info_button.bind("<Leave>", self.hide_info)
            self._info_button.bind("<ButtonPress>", self.show_info)
        else:
            self._frame.columnconfigure(500, weight=1)

    def _update_checkbutton_text(self, var=None, index=None, mode=None):
        val = self._display_var.get()
        if val == '0':
            text="Low"
        elif val == '1':
            text="High"
        else:
            text="Unknown"
        self._value_entry.config(text=text)

    def show_info(self, event=None):
        if hasattr(self, "_tooltip"):
            return

        widget = self._frame
        if hasattr(self, "_info_button"):
            widget = self._info_button

        x = y = 0
        x, y, cx, cy = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20

        self._tooltip = tk.Toplevel(widget)
        self._tooltip.wm_overrideredirect(True)
        self._tooltip.wm_geometry("+%d+%d" % (x, y))
        self._info_label = ttk.Label(self._tooltip, text=self._info.format(self._name), justify='left', wraplength=self._tooltip_width, relief='solid', borderwidth=1)
        self._info_label.pack(ipadx=1)

    def hide_info(self, event=None):
        if hasattr(self, "_tooltip"):
            self._tooltip.destroy()
            del self._tooltip
            del self._info_label

    def _write(self, func):
        if self.validate_register():
            func()
        else:
            self.send_message("Unable to write register {}, check that the value makes sense: '{}'".format(self._name, self._display_var.get()))

    def _toggle_bit(self, bit_idx):
        if self._enabled:
            value = int(self._display_var.get(), 0)
            self._display_var.set(hex_0fill(value ^ (1 << bit_idx), self._bits))

    def _update_binary_repr(self, var=None, index=None, mode=None):
        binary_string = ''.join(["0" for i in range(self._bits)])
        if self._display_var.get() != '' and self._display_var.get() != '0x':  # If value is set, decode the binary string
            binary_string = format(int(self._display_var.get(), 0), 'b')
            if len(binary_string) < self._bits:
                prepend = '0'*(self._bits-len(binary_string))
                binary_string = prepend + binary_string
        for bit in range(self._bits):
            value = binary_string[self._bits-1-bit]
            getattr(self, "_value_binary_bit{}".format(bit)).config(text=value)

    def invalid_register_value(self, string: str):
        self.send_message("Invalid value trying to be set for register {}: {}".format(self._name, string))

    def validate_register(self):
        if self._display_var.get() == "" or self._display_var.get() == "0x":
            return False
        self._display_var.set(hex_0fill(int(self._display_var.get(), 0), self._bits))
        return True