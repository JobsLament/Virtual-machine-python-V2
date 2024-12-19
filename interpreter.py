import struct
import xml.etree.ElementTree as ET
import argparse

MEMORY = [0] * 1024  # Простая модель памяти
ACCUMULATOR = 0      # Регистр-аккумулятор

def execute(binary_file, result_file, memory_range):
    global ACCUMULATOR

    with open(binary_file, 'rb') as f:
        binary_data = f.read()

    root = ET.Element("ExecutionResult")
    index = 0

    while index < len(binary_data):
        A = binary_data[index] & 0x3F
        if A == 19:  # LOAD_CONST
            B = struct.unpack_from('<I', binary_data, index)[0] >> 6
            ACCUMULATOR = B
            index += 4
        elif A == 16:  # LOAD_MEM
            B = struct.unpack_from('>I', binary_data, index + 1)[0]  # Big-endian
            ACCUMULATOR = MEMORY[B]
            index += 5

        elif A == 60:  # STORE_вMEM
            B = struct.unpack_from('<I', binary_data, index + 1)[0]
            MEMORY[B] = ACCUMULATOR
            index += 5
        elif A == 35:  # SHIFT_RIGHT
            B = struct.unpack_from('<I', binary_data, index + 1)[0]
            ACCUMULATOR >>= MEMORY[B]
            index += 5

        # Логирование в XML
        step = ET.SubElement(root, "Step")
        ET.SubElement(step, "Opcode").text = str(A)
        ET.SubElement(step, "Accumulator").text = str(ACCUMULATOR)

    # Сохранение указанного диапазона памяти
    start, end = map(int, memory_range.split(":"))
    memory_dump = ET.SubElement(root, "MemoryDump")
    for addr in range(start, end + 1):
        ET.SubElement(memory_dump, f"Address_{addr}").text = str(MEMORY[addr])

    tree = ET.ElementTree(root)
    tree.write(result_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interpreter for the VM.")
    parser.add_argument("binary", help="Path to the binary file")
    parser.add_argument("result", help="Path to the result XML file")
    parser.add_argument("memory_range", help="Memory range (start:end)")
    args = parser.parse_args()

    execute(args.binary, args.result, args.memory_range)
