#!/usr/bin/env python3
"""
Ассемблер для учебной виртуальной машины (УВМ)
Переводит текстовое представление программы в бинарный формат
"""

import json
import sys
import struct
import argparse
from pathlib import Path

class Assembler:
    """Ассемблер УВМ"""
    
    def __init__(self):
        self.program = []
        self.labels = {}
        
    def parse_json_program(self, json_data):
        """
        Парсинг программы в формате JSON
        """
        self.program = []
        
        for idx, line in enumerate(json_data):
            if not isinstance(line, dict):
                raise ValueError(f"Line {idx} must be a dictionary")
            
            instr_name = line.get("instruction")
            if not instr_name:
                raise ValueError(f"Line {idx}: missing 'instruction' field")
            
            # Проверяем операнды в зависимости от инструкции
            operands = line.get("operands", [])
            
            # Создаем промежуточное представление
            if instr_name == 'LOAD_CONST':
                if len(operands) != 1:
                    raise ValueError(f"Line {idx}: LOAD_CONST requires 1 operand")
                const_value = operands[0]
                if not 0 <= const_value < 1024:  # 10 бит
                    raise ValueError(f"Line {idx}: constant must be 10-bit value (0-1023)")
                self.program.append(('LOAD_CONST', const_value))
                
            elif instr_name == 'READ_MEM':
                if len(operands) != 1:
                    raise ValueError(f"Line {idx}: READ_MEM requires 1 operand")
                offset = operands[0]
                if not 0 <= offset < 1024:  # 10 бит
                    raise ValueError(f"Line {idx}: offset must be 10-bit value (0-1023)")
                self.program.append(('READ_MEM', offset))
                
            elif instr_name == 'WRITE_MEM':
                if len(operands) != 0:
                    raise ValueError(f"Line {idx}: WRITE_MEM requires 0 operands")
                self.program.append(('WRITE_MEM',))
                
            elif instr_name == 'DIV':
                if len(operands) != 1:
                    raise ValueError(f"Line {idx}: DIV requires 1 operand")
                address = operands[0]
                if not 0 <= address < 524288:  # 19 бит
                    raise ValueError(f"Line {idx}: address must be 19-bit value (0-524287)")
                self.program.append(('DIV', address))
            else:
                raise ValueError(f"Line {idx}: unknown instruction '{instr_name}'")
    
    def encode_instruction(self, instr_tuple):
        """Кодирование инструкции в бинарный формат (4 байта)"""
        instr_name = instr_tuple[0]
        
        if instr_name == 'LOAD_CONST':
            opcode = 43  # 0x2B
            const = instr_tuple[1]
            # Бит 0-6: opcode, бит 7-16: константа
            # Формат: (const << 7) | opcode
            word = ((const & 0x3FF) << 7) | opcode
            return struct.pack('<I', word)
            
        elif instr_name == 'READ_MEM':
            opcode = 120  # 0x78
            offset = instr_tuple[1]
            # Бит 0-6: opcode, бит 7-16: смещение
            word = ((offset & 0x3FF) << 7) | opcode
            return struct.pack('<I', word)
            
        elif instr_name == 'WRITE_MEM':
            opcode = 72  # 0x48
            # Только opcode
            return struct.pack('<I', opcode)
            
        elif instr_name == 'DIV':
            opcode = 121  # 0x79
            address = instr_tuple[1]
            # Бит 0-6: opcode, бит 7-25: адрес (19 бит)
            word = ((address & 0x7FFFF) << 7) | opcode
            return struct.pack('<I', word)
    
    def assemble(self, input_file, output_file, test_mode=False):
        """Основная функция ассемблирования"""
        try:
            # Чтение входного файла
            with open(input_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Парсинг программы
            self.parse_json_program(json_data)
            
            if test_mode:
                # Режим тестирования - вывод промежуточного представления
                print("Промежуточное представление программы:")
                print("-" * 40)
                for idx, instr in enumerate(self.program):
                    print(f"{idx}: {instr}")
                print("-" * 40)
                
                # Вывод в формате полей и значений как в спецификации
                print("\nБинарное представление (в формате спецификации):")
                print("-" * 40)
                for idx, instr in enumerate(self.program):
                    binary = self.encode_instruction(instr)
                    hex_bytes = ' '.join(f'0x{b:02X}' for b in binary)
                    print(f"{idx}: {hex_bytes}")
            
            # Запись бинарного файла
            with open(output_file, 'wb') as f:
                for instr in self.program:
                    binary_data = self.encode_instruction(instr)
                    f.write(binary_data)
            
            print(f"\nПрограмма успешно ассемблирована в {output_file}")
            print(f"Размер программы: {len(self.program) * 4} байт")
            
        except Exception as e:
            print(f"Ошибка ассемблирования: {e}")
            sys.exit(1)

def main():
    """Точка входа CLI"""
    parser = argparse.ArgumentParser(
        description='Ассемблер для учебной виртуальной машины (УВМ)',
        epilog='Пример: python assembler.py program.json program.bin --test'
    )
    
    parser.add_argument('input', help='Путь к исходному файлу с текстом программы (JSON)')
    parser.add_argument('output', help='Путь к двоичному файлу-результату')
    parser.add_argument('--test', action='store_true', 
                       help='Режим тестирования - вывод промежуточного представления')
    
    args = parser.parse_args()
    
    # Проверка существования входного файла
    if not Path(args.input).exists():
        print(f"Ошибка: файл '{args.input}' не найден")
        sys.exit(1)
    
    # Создание ассемблера и запуск
    assembler = Assembler()
    assembler.assemble(args.input, args.output, args.test)

if __name__ == "__main__":
    main()