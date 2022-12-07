import tkinter as tk
import logging

import i2c_gui

def main():
    root = tk.Tk()
    i2c_gui.__no_connect__ = True
    i2c_gui.set_platform(root.tk.call('tk', 'windowingsystem'))

    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s:%(name)s:%(message)s')
    logger = logging.getLogger("GUI_Logger")

    GUI = i2c_gui.Multi_GUI(root, logger)

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())

    root.mainloop()

if __name__ == "__main__":
    main()