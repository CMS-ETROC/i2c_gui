from __future__ import annotations

from .gui_helper import GUI_Helper

import tkinter as tk
import logging

class ScriptHelper(GUI_Helper):
    def __init__(self, logger: logging.Logger):
        # self._root = tk.Tk()  # Needed for some of the variables to work correctly
        super().__init__("Script Helper", tk.Tk(), logger)

    def _local_status_update(self, value):
        print("Updating local status to: {}".format(value))

    def send_message(self, message:str):
        print("GUI Message: {}".format(message))
    def get_all_indexed_blocks(self, indexer_info, block_name):
        indexed_blocks = {}
        for idx in range(len(indexer_info['vars'])):
            var = indexer_info['vars'][idx]
            min = indexer_info['min'][idx]
            max = indexer_info['max'][idx]

            old_indexed_blocks = indexed_blocks
            indexed_blocks = {}

            if var == "block" and min is None and max is None:
                param = block_name
                if len(old_indexed_blocks) == 0:
                    indexed_blocks[param] = {
                        'params': {'block': param},
                    }
                else:
                    for old in old_indexed_blocks:
                        indexed_blocks[old + ":" + param] = {}
                        indexed_blocks[old + ":" + param]['params'] = old_indexed_blocks[old]['params']
                        indexed_blocks[old + ":" + param]['params']['block'] = str(param)
            else:
                for val_idx in range(max - min):
                    i = min + val_idx
                    if len(old_indexed_blocks) == 0:
                        indexed_blocks[i] = {
                            'params': {var: i},
                        }
                    else:
                        for old in old_indexed_blocks:
                            indexed_blocks[old + ":" + str(i)] = {}
                            indexed_blocks[old + ":" + str(i)]['params'] = (old_indexed_blocks[old]['params']).copy()
                            indexed_blocks[old + ":" + str(i)]['params'][var] = i
        return indexed_blocks