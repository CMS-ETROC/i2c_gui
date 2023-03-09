from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..connection_controller import Connection_Controller
from ..gui_helper import GUI_Helper

from ..functions import hex_0fill

import tkinter as tk
import logging

class Address_Space_Controller(GUI_Helper):
    def __init__(self, parent: GUI_Helper, name, i2c_address, memory_size, i2c_controller: Connection_Controller, register_map, decoded_registers):
        super().__init__(parent, None, parent._logger)

        self._name = name
        self._i2c_address = i2c_address
        self._i2c_controller = i2c_controller
        self._memory_size = memory_size
        self._blocks = {}

        self._not_read = True

        self._memory = [None for val in range(self._memory_size)]

        self._display_vars = [tk.StringVar(value = "0", name="{}_{}_Reg{}".format(self._parent._unique_name, self._name, val)) for val in range(self._memory_size)]

        self._register_map = {}
        for block_name in register_map:
            if "Base Address" in register_map[block_name]:
                base_address = register_map[block_name]["Base Address"]
                self._blocks[block_name] = {
                    "Base Address": base_address,
                    "Length": len(register_map[block_name]["Registers"])  # Note: Assuming that all the listed registers in a block are contiguous in the memory space
                }

                for register in register_map[block_name]["Registers"]:
                    offset = register_map[block_name]["Registers"][register]["offset"]
                    full_address = base_address + offset
                    self._register_map[block_name + "/" + register] = full_address
                    self._display_vars[full_address].set(hex_0fill(register_map[block_name]["Registers"][register]['default'], 8))
            elif "Indexer" in register_map[block_name]:
                indexer_info = register_map[block_name]['Indexer']
                min_address, max_address, base_addresses = self._get_indexed_block_address_range(block_name, indexer_info, register_map[block_name]['Registers'])

                if max_address >= min_address:  # Note: even though not frequently used, a block covering the whole array is needed for bulk read/write operations
                    self._blocks[block_name] = {
                        "Base Address": min_address,
                        "Length": max_address - min_address + 1
                    }

                for block_ref in base_addresses:  # Note: it is a block ref and not a block name because this is a block array
                    self._blocks[block_ref] = {
                        "Base Address": base_addresses[block_ref]['base_address'],
                        "Length": len(register_map[block_name]["Registers"])  # Note: Assuming that all the listed registers in a block are contiguous in the memory space
                    }

                for register in register_map[block_name]["Registers"]:
                    offset = register_map[block_name]["Registers"][register]["offset"]
                    for base_name in base_addresses:
                        base_address = base_addresses[base_name]['base_address']
                        full_address = base_address + offset
                        full_register_name = base_name + "/" + register
                        self._register_map[full_register_name] = full_address
                        self._display_vars[full_address].set(hex_0fill(register_map[block_name]["Registers"][register]['default'], 8))
            else:
                self._logger.error("An impossible condition occured, there was a memory block defined which does not have a base address and does not have an indexer")

        self._decoded_display_vars = {}
        self._decoded_bit_size = {}
        if decoded_registers is not None:
            for block_name in decoded_registers:
                if block_name not in register_map:
                    self._logger.error("Skipping unknown block in register decoding map: {}".format(block_name))
                    continue
                for value in decoded_registers[block_name]:
                    decoding_info = decoded_registers[block_name][value]
                    value_bits = decoding_info['bits']

                    if "Base Address" in register_map[block_name]:
                        self._build_decoded_value(
                            value=value,
                            block_ref=block_name,
                            value_bits=value_bits,
                            decoding_position_info=decoding_info['position'],
                        )
                    elif "Indexer" in register_map[block_name]:
                        _, _, base_addresses = self._get_indexed_block_address_range(block_name, indexer_info, register_map[block_name]['Registers'])
                        for block_ref in base_addresses:  # Note: it is a block ref and not a block name because this is a block array
                            self._build_decoded_value(
                                value=value,
                                block_ref=block_ref,
                                value_bits=value_bits,
                                decoding_position_info=decoding_info['position'],
                            )
                    else:
                        self._logger.error("An impossible condition occured, there was a memory block defined which does not have a base address and does not have an indexer")

    def _build_decoded_value(self, value: str, block_ref: str, value_bits: int, decoding_position_info: list[tuple]):
        self._decoded_display_vars[block_ref + "/" + value] = tk.StringVar(name="{}_{}_{}_{}".format(self._parent._unique_name, self._name, block_ref, value))
        self._decoded_bit_size[block_ref + "/" + value] = value_bits

        for regInfo in decoding_position_info:
            register = regInfo[0]

            register_var = self._display_vars[self._register_map[block_ref + "/" + register]]
            self._update_decoded_value(block_ref, value, value_bits, regInfo)
            # Note: Save ? these callbacks in case they need to be handled later
            register_var.trace_add('write', lambda var, index, mode, block_ref=block_ref, value=value, value_bits=value_bits, position=regInfo:self._update_decoded_value(block_ref, value, value_bits, position))
            self._decoded_display_vars[block_ref + "/" + value].trace_add('write', lambda var, index, mode, block_ref=block_ref, value=value, value_bits=value_bits, position=regInfo:self._update_register(block_ref, value, value_bits, position))

    def _get_indexed_block_address_range(self, block_name, indexer_info, register_map):
        indexer_function = indexer_info['function']

        registers = {}
        for idx in range(len(indexer_info['vars'])):
            var = indexer_info['vars'][idx]
            min = indexer_info['min'][idx]
            max = indexer_info['max'][idx]

            old_registers = registers
            registers = {}

            if var == "block" and min is None and max is None:
                param = block_name
                if len(old_registers) == 0:
                    registers[param] = {
                        'params': {'block': param},
                    }
                else:
                    for old in old_registers:
                        registers[old + ":" + param] = {}
                        registers[old + ":" + param]['params'] = old_registers[old]['params']
                        registers[old + ":" + param]['params']['block'] = str(param)
            else:
                for val_idx in range(max - min):
                    i = min + val_idx
                    if len(old_registers) == 0:
                        registers[i] = {
                            'params': {var: i},
                        }
                    else:
                        for old in old_registers:
                            registers[old + ":" + str(i)] = {}
                            registers[old + ":" + str(i)]['params'] = (old_registers[old]['params']).copy()
                            registers[old + ":" + str(i)]['params'][var] = i

        min_address = None
        max_address = None
        for key in registers:
            address = indexer_function(**(registers[key]['params']))
            registers[key]['base_address'] = address
            if min_address is None or address < min_address:
                min_address = address
            if max_address is None or address > max_address:
                max_address = address

        max_offset = None
        for register in register_map:
            offset = register_map[register]['offset']
            if max_offset is None or offset > max_offset:
                max_offset = offset

        return min_address, max_address + max_offset, registers

    @property
    def is_modified(self):
        if self._i2c_address is None or self._not_read:
            return "Unknown"

        for idx  in range(self._memory_size):
            value = self._display_vars[idx].get()
            if value == "" or value == "0x":
                value = 0
            else:
                value = int(value, 0)
            if value != self._memory[idx]:
                return True
        return False

    def _update_register(self, block, value, bits, position):
        if hasattr(self, "_updating_from_register"):  # Avoid an infinite loop where the two variables trigger each other
            return

        self._updating_from_decoded_value = True

        register_min_idx, register_max_idx = self._get_bit_index_min_max(position[1], 8)
        value_min_idx,    value_max_idx    = self._get_bit_index_min_max(position[2], bits)

        register_repr = self._build_bit_repr(self._display_vars[self._register_map[block + "/" + position[0]]], 8)
        value_repr = self._build_bit_repr(self._decoded_display_vars[block + "/" + value], bits)

        register_repr = [i for i in register_repr]
        value_repr = [i for i in value_repr]
        register_repr[register_min_idx:register_max_idx] = value_repr[value_min_idx:value_max_idx]
        register_repr = ''.join(register_repr)

        register_repr = '0b' + register_repr
        self._display_vars[self._register_map[block + "/" + position[0]]].set(hex_0fill(int(register_repr, 0), 8))

        del self._updating_from_decoded_value

    def _update_decoded_value(self, block, value, bits, position):
        if hasattr(self, "_updating_from_decoded_value"):  # Avoid an infinite loop where the two variables trigger each other
            return

        self._updating_from_register = True

        register_min_idx, register_max_idx = self._get_bit_index_min_max(position[1], 8)
        value_min_idx,    value_max_idx    = self._get_bit_index_min_max(position[2], bits)

        register_repr = self._build_bit_repr(self._display_vars[self._register_map[block + "/" + position[0]]], 8)
        value_repr = self._build_bit_repr(self._decoded_display_vars[block + "/" + value], bits)

        register_repr = [i for i in register_repr]
        value_repr = [i for i in value_repr]
        value_repr[value_min_idx:value_max_idx] = register_repr[register_min_idx:register_max_idx]
        value_repr = ''.join(value_repr)

        if bits == 1:
            self._decoded_display_vars[block + "/" + value].set(value_repr)
        else:
            value_repr = '0b' + value_repr
            self._decoded_display_vars[block + "/" + value].set(hex_0fill(int(value_repr, 0), bits))

        del self._updating_from_register

    def _build_bit_repr(self, var: tk.Variable, bit_length: int=8):
        binary_string = ''.join(["0" for i in range(bit_length)])
        value = var.get()

        if value != "" and value != "0x":
            binary_string = format(int(value, 0), 'b')
            if len(binary_string) < bit_length:
                prepend = '0'*(bit_length-len(binary_string))
                binary_string = prepend + binary_string

        return binary_string

    def _get_bit_index_min_max(self, index: str, bit_size: int=8):
        bit_idx_limits = index.split('-')

        for idx in range(len(bit_idx_limits)):
            bit_idx_limits[idx] = int(bit_idx_limits[idx])

        if len(bit_idx_limits) == 1:
            max_val = bit_size - bit_idx_limits[0]
            min_val = max_val - 1
        else:
            min_val = bit_size - bit_idx_limits[0] - 1
            max_val = bit_size - bit_idx_limits[1]

        return (min_val, max_val)

    def update_i2c_address(self, address: int):
        if address != self._i2c_address:
            self._i2c_address = address
            self._not_read = True

            if address is not None:
                self._logger.info("Updated address space '{}' to the I2C address {}".format(self._name, hex_0fill(address, 7)))
            else:
                self._logger.info("Reset the I2C address for the address space '{}'".format(self._name))

    def get_memory(self, register_name):
        return self._memory[self._register_map[register_name]]

    def get_display_var(self, register_name):
        return self._display_vars[self._register_map[register_name]]

    def get_decoded_display_var(self, value_name):
        return self._decoded_display_vars[value_name]

    def get_decoded_bit_size(self, value_name):
        return self._decoded_bit_size[value_name]

    def read_all(self):
        if self._i2c_address is None:
            self._logger.info("Unable to read address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Reading the full '{}' address space".format(self._name))

        self._memory = self._i2c_controller.read_device_memory(self._i2c_address, 0, self._memory_size)
        for idx in range(self._memory_size):
            self._display_vars[idx].set(hex_0fill(self._memory[idx], 8))
        self._not_read = False

        self._parent.update_whether_modified()

    def write_all(self, write_check: bool = True):
        if self._i2c_address is None:
            self._logger.info("Unable to write address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Writing the full '{}' address space".format(self._name))

        for idx in range(self._memory_size):
            self._memory[idx] = int(self._display_vars[idx].get(), 0)
        self._i2c_controller.write_device_memory(self._i2c_address, 0, self._memory)

        if write_check:
            self._memory = self._i2c_controller.read_device_memory(self._i2c_address, 0, self._memory_size)
            failed = []
            for i in range(self._memory_size):
                if self._memory[i] != int(self._display_vars[i].get(), 0):
                    failed += [i]
                    # self._display_vars[i].set(hex_0fill(self._memory[i], 8))
            if len(failed) != 0:
                failed = ["0x{:0x}".format(i) for i in failed]
                self.send_message("Failure to write the full {} address space (I2C address 0x{:0x}). The following register addresses failed to write: {}".format(self._name, self._i2c_address, ', '.join(failed)))

        self._parent.update_whether_modified()

    def read_memory_register(self, address):
        if self._i2c_address is None:
            self._logger.info("Unable to read address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Reading register at address {} in the address space '{}'".format(address, self._name))

        tmp = self._i2c_controller.read_device_memory(self._i2c_address, address, 1)
        self._memory[address] = tmp[0]
        self._display_vars[address].set(hex_0fill(tmp[0], 8))

        self._parent.update_whether_modified()

    def write_memory_register(self, address, write_check: bool = True):
        if self._i2c_address is None:
            self._logger.info("Unable to write address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Writing register at address {} in the address space '{}'".format(address, self._name))

        self._memory[address] = int(self._display_vars[address].get(), 0)
        self._i2c_controller.write_device_memory(self._i2c_address, address, [self._memory[address]])

        if write_check:
            tmp = self._i2c_controller.read_device_memory(self._i2c_address, address, 1)
            if self._memory[address] != tmp[0]:
                self.send_message("Failure to write register at address 0x{:0x} in the {} address space (I2C address 0x{:0x})".format(address, self._name, self._i2c_address))
                self._memory[address] = tmp[0]
                # self._display_vars[address].set(hex_0fill(tmp[0], 8))

        self._parent.update_whether_modified()

    def read_memory_block(self, address, data_size):
        if self._i2c_address is None:
            self._logger.info("Unable to read address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Reading a block of {} bytes starting at address {} in the address space '{}'".format(data_size, address, self._name))

        tmp = self._i2c_controller.read_device_memory(self._i2c_address, address, data_size)
        for i in range(data_size):
            self._memory[address+i] = tmp[i]
            self._display_vars[address+i].set(hex_0fill(tmp[i], 8))

        self._parent.update_whether_modified()

    def write_memory_block(self, address, data_size, write_check: bool = True):
        if self._i2c_address is None:
            self._logger.info("Unable to write address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Writing a block of {} bytes starting at address {} in the address space '{}'".format(data_size, address, self._name))

        for i in range(data_size):
            self._memory[address+i] = int(self._display_vars[address+i].get(), 0)
        self._i2c_controller.write_device_memory(self._i2c_address, address, self._memory[address:address+data_size])

        if write_check:
            tmp = self._i2c_controller.read_device_memory(self._i2c_address, address, data_size)
            failed = []
            for i in range(data_size):
                if self._memory[address+i] != tmp[i]:
                    failed += [address+i]
                    self._memory[address+i] = tmp[i]
                    # self._display_vars[address+i].set(hex_0fill(tmp[i], 8))
            if len(failed) != 0:
                failed = ["0x{:0x}".format(i) for i in failed]
                self.send_message("Failure to write memory block at address 0x{:0x} with length {} in the {} address space (I2C address 0x{:0x}). The following register addresses failed to write: {}".format(address, data_size, self._name, self._i2c_address, ', '.join(failed)))

        self._parent.update_whether_modified()

    def read_block(self, block_name):
        if self._i2c_address is None:
            self._logger.info("Unable to read address space '{}' because the i2c address is not set".format(self._name))
            return

        block = self._blocks[block_name]
        self._logger.info("Attempting to read block {}".format(block_name))

        self.read_memory_block(block["Base Address"], block["Length"])

    def write_block(self, block_name, write_check: bool = True):
        if self._i2c_address is None:
            self._logger.info("Unable to write address space '{}' because the i2c address is not set".format(self._name))
            return

        block = self._blocks[block_name]
        self._logger.info("Attempting to write block {}".format(block_name))

        self.write_memory_block(block["Base Address"], block["Length"], write_check)

    def read_register(self, block_name, register_name):
        if self._i2c_address is None:
            self._logger.info("Unable to read address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Attempting to read register {} in block {}".format(register_name, block_name))

        self.read_memory_register(self._register_map[block_name + "/" + register_name])

    def write_register(self, block_name, register_name, write_check: bool = True):
        if self._i2c_address is None:
            self._logger.info("Unable to write address space '{}' because the i2c address is not set".format(self._name))
            return

        self._logger.info("Attempting to write register {} in block {}".format(register_name, block_name))

        self.write_memory_register(self._register_map[block_name + "/" + register_name], write_check)

# TODO: Add a check after writing where the values are read and compared
