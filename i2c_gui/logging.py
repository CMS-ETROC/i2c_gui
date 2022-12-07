from __future__ import annotations

from .gui_helper import GUI_Helper
from .base_gui import Base_GUI

import tkinter as tk
import tkinter.ttk as ttk  # For themed widgets (gives a more native visual to the elements)
import logging
import io

class Logging_Helper(GUI_Helper):
    _parent: Base_GUI
    def __init__(self, parent: Base_GUI):
        super().__init__(parent, None, parent._logger)

        self._do_logging = False
        self._logger.disabled = True

        self._stream = io.StringIO()
        self._stream_handler = logging.StreamHandler(self._stream)
        self._stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s:%(name)s:%(message)s'))
        self._logger.handlers.clear()

        self._logging_window_status_var = tk.StringVar()
        self._logging_window_status_var.set("Logging Disabled")

        self._autorefresh_var = tk.BooleanVar(value=False)

    @property
    def is_logging(self):
        return self._do_logging

    @is_logging.setter
    def is_logging(self, value):
        if value not in [True, False]:
            raise TypeError("Logging can only be true or false")

        self._do_logging = value

        if self._do_logging:
            if self._stream_handler not in self._logger.handlers:
                self._logger.addHandler(self._stream_handler)
            self._logger.disabled = False
            self._logging_window_status_var.set("Logging Enabled")
        else:
            if self._stream_handler in self._logger.handlers:
                self._logger.removeHandler(self._stream_handler)
            self._logger.disabled = True
            self._logging_window_status_var.set("Logging Disabled")

    def get_log(self):
        return self._stream.getvalue()

    def display_logging(self):
        if hasattr(self, "_logging_window"):
            self._logger.info("Logging window already open")
            return

        self._logging_window = tk.Toplevel(self._parent._root)
        self._logging_window.title(self._parent._title + " - Event Log")
        self._logging_window.protocol('WM_DELETE_WINDOW', self.close_logging_window)
        self._logging_window.columnconfigure(100, weight=1)
        self._logging_window.rowconfigure(100, weight=1)

        self._frame = ttk.Frame(self._logging_window, padding="5 5 5 5")
        self._frame.grid(column=100, row=100, sticky=(tk.N, tk.W, tk.E, tk.S))
        self._frame.columnconfigure(100, weight=1)
        self._frame.rowconfigure(100, weight=1)

        self._text_frame = ttk.Frame(self._frame)
        self._text_frame.grid(column=100, row=100, sticky=(tk.N, tk.W, tk.E, tk.S))
        self._text_frame.columnconfigure(100, weight=1)
        self._text_frame.rowconfigure(100, weight=1)

        self._text_display = tk.Text(self._text_frame, state='disabled', width=150, wrap='none')
        self._text_display.grid(column=100, row=100, sticky=(tk.N, tk.W, tk.E, tk.S))

        self._scrollbar = ttk.Scrollbar(self._text_frame, command=self._text_display.yview)
        self._scrollbar.grid(row=100, column=101, sticky='nsew')
        self._text_display.config(yscrollcommand=self._scrollbar.set)

        self._control_frame = ttk.Frame(self._frame)
        self._control_frame.grid(column=100, row=200, sticky=(tk.N, tk.W, tk.E, tk.S))

        self._toggle_logging_button = ttk.Button(self._control_frame, text="Enable Logging", command=self.toggle_logging)
        self._toggle_logging_button.grid(column=100, row=100, sticky=(tk.W, tk.E), padx=(0,5))

        self._clear_logging_button = ttk.Button(self._control_frame, text="Clear Log", command=self.clear_log)
        self._clear_logging_button.grid(column=110, row=100, sticky=(tk.W, tk.E), padx=(0,5))

        self._logging_status_label = ttk.Label(self._control_frame, textvariable=self._logging_window_status_var)
        self._logging_status_label.grid(column=200, row=100, sticky=(tk.W, tk.E), padx=(0,30))
        self._control_frame.columnconfigure(200, weight=1)

        self._autorefresh_check = ttk.Checkbutton(self._control_frame, text="Auto-refresh", variable=self._autorefresh_var, command=self.toggle_autorefresh)
        self._autorefresh_check.grid(column=300, row=100, sticky=(tk.W, tk.E), padx=(0,10))

        self._refresh_button = ttk.Button(self._control_frame, text="Refresh", command=self.refresh_logging)
        self._refresh_button.grid(column=400, row=100, sticky=(tk.W, tk.E))

        self._logging_window.update()
        self._logging_window.minsize(self._logging_window.winfo_width(), self._logging_window.winfo_height())

    def close_logging_window(self):
        if not hasattr(self, "_logging_window"):
            self._logger.info("Logging window does not exist")
            return

        self._logging_window.destroy()
        del self._logging_window

    def clear_log(self):
        self._stream.truncate(0)
        self._stream.seek(0)
        self.refresh_logging()

    def toggle_logging(self):
        self.is_logging = not self.is_logging

        button_text = "Enable Logging"
        if self.is_logging:
            button_text = "Disable Logging"

        self._toggle_logging_button.config(text=button_text)

    def toggle_autorefresh(self):
        autorefresh = self._autorefresh_var.get()
        if autorefresh:
            self.send_message("Turn on logging auto-refresh")
            self.autorefresh_logging()
            self._refresh_button.configure(state='disabled', text="Disabled")
        else:
            self.send_message("Turn off logging auto-refresh")
            self._refresh_button.configure(state='normal', text="Refresh")

    def autorefresh_logging(self):
        self.refresh_logging()

        autorefresh = self._autorefresh_var.get()
        if autorefresh:
            self._text_display.after(500, self.autorefresh_logging)

    def refresh_logging(self):
        pos = self._scrollbar.get()
        vw = self._text_display.yview()

        #print(pos)
        #print(vw)
        # TODO: Scrollbar is still jumping around when updating. It is related to when the lines of text wrap to the next line
        # Disabling line wrapping seems to have "fixed" (hidden) the issue

        self._text_display.configure(state='normal')
        self._text_display.delete("1.0", tk.END)
        self._text_display.insert('end', self.get_log())
        self._text_display.configure(state='disabled')
        #self._text_display.yview_moveto(pos[0])
        self._text_display.yview_moveto(vw[0])