import struct
import xml.etree.ElementTree as ET
import argparse

# Таблица кодов операций
OPCODES = {
    'LOAD_CONST': 19,
    'LOAD_MEM': 16,
    'STORE_MEM': 60,
    'SHIFT_RIGHT': 35,
}

def assemble(input_file, output_file, log_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    binary_data = bytearray()
    root = ET.Element("Log")

    for line in lines:
        parts = line.strip().split()
        opcode_name = parts[0]
        A = OPCODES[opcode_name]
        B = int(parts[1])

        # Формирование бинарного кода
        if opcode_name == 'LOAD_MEM' or opcode_name == 'STORE_MEM':
            # Упаковываем корректно, учитывая 6-битное поле A и старшие биты B
            first_byte = (A & 0x3F) | ((B & 0x3) << 6)
            command = struct.pack('<B I', first_byte, B >> 2)
        elif opcode_name == 'LOAD_CONST' or opcode_name == 'SHIFT_RIGHT':
            # Для других команд, используем 4-байтный little-endian формат
            command = struct.pack('<I', (A & 0x3F) | (B << 6))
        else:
            raise ValueError(f"Неизвестная команда: {opcode_name}")

        binary_data.extend(command)

        # Логирование в XML
        instruction = ET.SubElement(root, "Instruction")
        ET.SubElement(instruction, "Opcode").text = opcode_name
        ET.SubElement(instruction, "A").text = str(A)
        ET.SubElement(instruction, "B").text = str(B)
        ET.SubElement(instruction, "Bytes").text = command.hex()

    with open(output_file, 'wb') as f:
        f.write(binary_data)

    tree = ET.ElementTree(root)
    tree.write(log_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assembler for the VM.")
    parser.add_argument("input", help="Path to the input file")
    parser.add_argument("output", help="Path to the output binary file")
    parser.add_argument("log", help="Path to the log XML file")
    args = parser.parse_args()

    assemble(args.input, args.output, args.log)
