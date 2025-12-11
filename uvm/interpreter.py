#!/usr/bin/env python3
"""
Интерпретатор для учебной виртуальной машины (УВМ)
"""

import sys
import struct
import argparse
from pathlib import Path

class Memory:
    """Память УВМ"""
    
    def __init__(self, size=1024 * 1024):
        self.size = size
        self.memory = bytearray(size)
        self.stack = []
        
    def read_word(self, address):
        """Чтение слова (4 байта) из памяти"""
        if 0 <= address < self.size - 3:
            return struct.unpack('<I', self.memory[address:address+4])[0]
        else:
            raise MemoryError(f"Попытка чтения за пределами памяти: 0x{address:08X}")
    
    def write_word(self, address, value):
        """Запись слова (4 байта) в память"""
        if 0 <= address < self.size - 3:
            struct.pack_into('<I', self.memory, address, value & 0xFFFFFFFF)
        else:
            raise MemoryError(f"Попытка записи за пределами памяти: 0x{address:08X}")
    
    def push(self, value):
        """Помещение значения на стек"""
        self.stack.append(value)
    
    def pop(self):
        """Снятие значения со стека"""
        if not self.stack:
            raise RuntimeError("Попытка чтения из пустого стека")
        return self.stack.pop()

class Interpreter:
    """Интерпретатор УВМ"""
    
    def __init__(self, memory_size=1024 * 1024):
        self.memory = Memory(memory_size)
        self.ip = 0  # Instruction pointer
        self.running = False
        
    def load_program(self, program_file):
        """Загрузка программы из бинарного файла"""
        with open(program_file, 'rb') as f:
            data = f.read()
        
        if len(data) > self.memory.size:
            raise MemoryError("Программа слишком большая для памяти")
        
        self.memory.memory[:len(data)] = data
        self.ip = 0
        print(f"Загружена программа размером {len(data)} байт")
    
    def decode_instruction(self):
        """Декодирование инструкции по текущему IP"""
        if self.ip >= self.memory.size - 3:
            return None, None, None
        
        # Чтение слова (4 байта)
        word_bytes = self.memory.memory[self.ip:self.ip+4]
        if len(word_bytes) < 4:
            return None, None, None
        
        word = struct.unpack('<I', word_bytes)[0]
        
        # Извлечение полей
        opcode = word & 0x7F  # Бит 0-6
        field_b_10bit = (word >> 7) & 0x3FF  # Бит 7-16 (10 бит)
        field_b_19bit = (word >> 7) & 0x7FFFF  # Бит 7-25 (19 бит)
        
        return opcode, field_b_10bit, field_b_19bit
    
    def execute_instruction(self, opcode, field_b_10bit, field_b_19bit):
        """Выполнение декодированной инструкции"""
        # LOAD_CONST
        if opcode == 43:
            self.memory.push(field_b_10bit)
            self.ip += 4
            print(f"LOAD_CONST: загружена константа {field_b_10bit} на стек")
            
        # READ_MEM
        elif opcode == 120:
            if not self.memory.stack:
                raise RuntimeError("Стек пуст для чтения адреса")
            address = self.memory.pop()
            value = self.memory.read_word(address + field_b_10bit)
            self.memory.push(value)
            self.ip += 4
            print(f"READ_MEM: прочитано значение 0x{value:08X} из адреса {address}+{field_b_10bit}")
            
        # WRITE_MEM
        elif opcode == 72:
            if not self.memory.stack:
                raise RuntimeError("Стек пуст для получения значения")
            value = self.memory.pop()
            if not self.memory.stack:
                raise RuntimeError("Стек пуст для получения адреса")
            address = self.memory.pop()
            self.memory.write_word(address, value)
            self.ip += 4
            print(f"WRITE_MEM: записано значение 0x{value:08X} по адресу 0x{address:08X}")
            
        # DIV
        elif opcode == 121:
            if not self.memory.stack:
                raise RuntimeError("Стек пуст для деления")
            dividend = self.memory.pop()
            divisor_addr = field_b_19bit
            divisor = self.memory.read_word(divisor_addr)
            
            if divisor == 0:
                raise ZeroDivisionError("Деление на ноль")
            
            result = dividend // divisor  # Целочисленное деление
            self.memory.push(result)
            self.ip += 4
            print(f"DIV: {dividend} / {divisor} = {result} (адрес делителя: {divisor_addr})")
            
        else:
            # Если opcode == 0, значит достигли конца программы
            if opcode == 0:
                self.running = False
                return
            raise ValueError(f"Неизвестный код операции: 0x{opcode:02X}")
    
    def get_dump_xml(self, start_addr, end_addr):
        """Получение дампа памяти в формате XML"""
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<memory_dump>')
        xml.append(f'  <range start="0x{start_addr:08X}" end="0x{end_addr:08X}"/>')
        xml.append('  <data>')
        
        for addr in range(start_addr, end_addr, 16):
            line_end = min(addr + 16, end_addr)
            hex_bytes = []
            ascii_chars = []
            
            for i in range(addr, line_end):
                byte = self.memory.memory[i]
                hex_bytes.append(f'{byte:02X}')
                ascii_chars.append(chr(byte) if 32 <= byte < 127 else '.')
            
            hex_str = ' '.join(hex_bytes)
            ascii_str = ''.join(ascii_chars)
            xml.append(f'    <line addr="0x{addr:08X}">')
            xml.append(f'      <hex>{hex_str}</hex>')
            xml.append(f'      <ascii>{ascii_str}</ascii>')
            xml.append('    </line>')
        
        xml.append('  </data>')
        xml.append('</memory_dump>')
        return '\n'.join(xml)
    
    def run(self, program_file, dump_file=None, dump_range=None):
        """Запуск выполнения программы"""
        try:
            self.load_program(program_file)
            
            self.running = True
            instruction_count = 0
            
            print("Начало выполнения программы...")
            print("-" * 50)
            
            while self.running and self.ip < self.memory.size - 3:
                opcode, field_b_10bit, field_b_19bit = self.decode_instruction()
                
                if opcode is None:
                    break
                
                if opcode == 0:  # Конец программы
                    break
                
                self.execute_instruction(opcode, field_b_10bit, field_b_19bit)
                instruction_count += 1
                
                if instruction_count > 10000:
                    print("Превышено максимальное количество инструкций")
                    break
            
            print("-" * 50)
            print(f"Выполнение завершено.")
            print(f"Всего выполнено инструкций: {instruction_count}")
            print(f"Содержимое стека: {self.memory.stack}")
            
            if dump_file and dump_range:
                start_addr, end_addr = dump_range
                dump_xml = self.get_dump_xml(start_addr, end_addr)
                with open(dump_file, 'w', encoding='utf-8') as f:
                    f.write(dump_xml)
                print(f"Дамп памяти сохранен в {dump_file}")
                
        except Exception as e:
            print(f"Ошибка выполнения: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def parse_dump_range(range_str):
    """Парсинг диапазона адресов для дампа"""
    if ':' in range_str:
        start_str, end_str = range_str.split(':')
        return int(start_str, 0), int(end_str, 0)
    else:
        size = int(range_str, 0)
        return 0, size

def main():
    parser = argparse.ArgumentParser(description='Интерпретатор УВМ')
    parser.add_argument('program', help='Путь к бинарному файлу программы')
    parser.add_argument('--dump', help='Путь для сохранения дампа памяти (XML)')
    parser.add_argument('--range', help='Диапазон адресов для дампа (start:end или size)')
    
    args = parser.parse_args()
    
    if not Path(args.program).exists():
        print(f"Ошибка: файл программы '{args.program}' не найден")
        sys.exit(1)
    
    dump_range = None
    if args.dump:
        if not args.range:
            print("Ошибка: для дампа необходимо указать диапазон адресов")
            sys.exit(1)
        try:
            dump_range = parse_dump_range(args.range)
        except ValueError as e:
            print(f"Ошибка парсинга диапазона: {e}")
            sys.exit(1)
    
    interpreter = Interpreter()
    interpreter.run(args.program, args.dump, dump_range)

if __name__ == "__main__":
    main()