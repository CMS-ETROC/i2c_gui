from __future__ import annotations

from .gui_helper import GUI_Helper
from .functions import hex_0fill

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging

class Register_Display(GUI_Helper):
    _parent: GUI_Helper
    def __init__(self, parent: GUI_Helper, register_name: str, display_var: tk.StringVar):
        super().__init__(parent, None, parent._logger)

        self._name = register_name
        self._enabled = False
        self._display_var = display_var
        self._shadow_var = None

    @property
    def shadow_var(self):
        return self._shadow_var

    @shadow_var.setter
    def shadow_var(self, val):
        if val is None or isinstance(val, tk.Variable):
            self._shadow_var = val
        else:
            raise RuntimeError("Wrong type for shadow variable: '{}'".format(type(val)))

    def enable(self):
        self._enabled = True
        if hasattr(self, "_value_entry"):
            self._value_entry.config(state="normal")
        if hasattr(self, "_read_button"):
            self._read_button.config(state="normal")
        if hasattr(self, "_write_button"):
            self._write_button.config(state="normal")

    def disable(self):
        self._enabled = False
        if hasattr(self, "_value_entry"):
            self._value_entry.config(state="disabled")
        if hasattr(self, "_read_button"):
            self._read_button.config(state="disabled")
        if hasattr(self, "_write_button"):
            self._write_button.config(state="disabled")

    def set_position(self, col: int, row: int):
        self._frame.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S), padx=5, pady=5)

    def get_required_size(self):
        return (self._frame.winfo_reqwidth(), self._frame.winfo_reqheight())

    def get_size(self):
        return (self._frame.winfo_width(), self._frame.winfo_height())

    def prepare_display(self, element: tk.Tk, col: int, row: int, read_function=None, write_function=None):
        self._frame = ttk.LabelFrame(element, text=self._name)
        self.set_position(col, row)

        state = 'disabled'
        if self._enabled:
            state = 'normal'

        self._value_label = ttk.Label(self._frame, text="Value:")
        self._value_label.grid(column=100, row=100, sticky=tk.E)

        self._value_entry = ttk.Entry(self._frame, textvariable=self._display_var, state=state, width=5)
        self._value_entry.grid(column=200, row=100, sticky=tk.W)

        from .functions import validate_8bit_register
        self._register_validate_cmd = (self._frame.register(validate_8bit_register), '%P')
        self._register_invalid_cmd  = (self._frame.register(self.invalid_register_value), '%P')
        self._value_entry.config(validate='key', validatecommand=self._register_validate_cmd, invalidcommand=self._register_invalid_cmd)


        self._value_binary_label = ttk.Label(self._frame, text="Binary:")
        self._value_binary_label.grid(column=100, row=200, sticky=tk.E)

        self._value_binary_frame = ttk.Frame(self._frame)
        self._value_binary_frame.grid(column=200, row=200, sticky=(tk.W, tk.S, tk.N), padx=0, pady=0)
        self._frame.rowconfigure(200, weight=1)
        self._value_binary_frame.rowconfigure(100, weight=1)

        self._value_binary_prefix = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0b")
        self._value_binary_prefix.grid(column=100, row=100)

        self._value_binary_bit7 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit7.grid(column=200, row=100)

        self._value_binary_bit6 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit6.grid(column=300, row=100)

        self._value_binary_bit5 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit5.grid(column=400, row=100)

        self._value_binary_bit4 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit4.grid(column=500, row=100)

        self._value_binary_bit3 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit3.grid(column=600, row=100)

        self._value_binary_bit2 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit2.grid(column=700, row=100)

        self._value_binary_bit1 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit1.grid(column=800, row=100)

        self._value_binary_bit0 = ttk.Label(self._value_binary_frame, font='TkFixedFont', text="0")
        self._value_binary_bit0.grid(column=900, row=100)

        self._value_binary_bit7.bind("<Button-1>", lambda e:self._toggle_bit(7))
        self._value_binary_bit6.bind("<Button-1>", lambda e:self._toggle_bit(6))
        self._value_binary_bit5.bind("<Button-1>", lambda e:self._toggle_bit(5))
        self._value_binary_bit4.bind("<Button-1>", lambda e:self._toggle_bit(4))
        self._value_binary_bit3.bind("<Button-1>", lambda e:self._toggle_bit(3))
        self._value_binary_bit2.bind("<Button-1>", lambda e:self._toggle_bit(2))
        self._value_binary_bit1.bind("<Button-1>", lambda e:self._toggle_bit(1))
        self._value_binary_bit0.bind("<Button-1>", lambda e:self._toggle_bit(0))
        self._display_var.trace('w', self._update_binary_repr)


        if read_function is not None:
            self._read_button = ttk.Button(self._frame, text="R", state=state, command=read_function, width=1.5)
            self._read_button.grid(column=400, row=100, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(10,0))

        if write_function is not None:
            self._write_button = ttk.Button(self._frame, text="W", state=state, command=lambda func=write_function: self._write(func), width=1.5)
            self._write_button.grid(column=400, row=200, sticky=(tk.N, tk.W, tk.E, tk.S), padx=(10,0))


        self._frame.columnconfigure(0, weight=1)
        self._frame.columnconfigure(500, weight=1)

        self._update_binary_repr()

    def _write(self, func):
        if self.validate_register():
            func()
        else:
            self.send_message("Unable to write register {}, check that the value makes sense: '{}'".format(self._name, self._display_var.get()))


    def _toggle_bit(self, bit_idx):
        if self._enabled:
            value = int(self._display_var.get(), 0)
            self._display_var.set(hex_0fill(value ^ (1 << bit_idx), 8))

    def _update_binary_repr(self, var=None, index=None, mode=None):
        binary_string = "00000000"
        if self._display_var.get() != '' and self._display_var.get() != '0x':  # If value is set, decode the binary string
            binary_string = format(int(self._display_var.get(), 0), 'b')
            if len(binary_string) < 8:
                prepend = '0'*(8-len(binary_string))
                binary_string = prepend + binary_string
        for bit in range(8):
            value = binary_string[7-bit]
            getattr(self, "_value_binary_bit{}".format(bit)).config(text=value)

        self._parent.update_whether_modified()

    def invalid_register_value(self, string: str):
        self.send_message("Invalid value trying to be set for register {}: {}".format(self._name, string))

    def validate_register(self):
        if self._display_var.get() == "" or self._display_var.get() == "0x":
            return False
        self._display_var.set(hex_0fill(int(self._display_var.get(), 0), 8))
        return True