"""
Модель памяти УВМ
Объединенная память команд и данных
"""

import struct

class Memory:
    """Память УВМ"""
    
    def __init__(self, size=1024 * 1024):  # 1 МБ памяти
        self.size = size
        self.memory = bytearray(size)
        self.stack = []  # Стек машины
        
    def read_byte(self, address):
        """Чтение байта из памяти"""
        if 0 <= address < self.size:
            return self.memory[address]
        else:
            raise MemoryError(f"Попытка чтения за пределами памяти: 0x{address:08X}")
    
    def read_word(self, address):
        """Чтение слова (4 байта) из памяти"""
        if 0 <= address < self.size - 3:
            return struct.unpack('<I', self.memory[address:address+4])[0]
        else:
            raise MemoryError(f"Попытка чтения за пределами памяти: 0x{address:08X}")
    
    def write_byte(self, address, value):
        """Запись байта в память"""
        if 0 <= address < self.size:
            self.memory[address] = value & 0xFF
        else:
            raise MemoryError(f"Попытка записи за пределами памяти: 0x{address:08X}")
    
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
    
    def peek(self):
        """Просмотр вершины стека без извлечения"""
        if not self.stack:
            raise RuntimeError("Попытка чтения из пустого стека")
        return self.stack[-1]
    
    def get_dump_xml(self, start_addr, end_addr):
        """Получение дампа памяти в формате XML"""
        if start_addr < 0 or end_addr > self.size or start_addr >= end_addr:
            raise ValueError("Неверный диапазон адресов")
        
        xml = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml.append('<memory_dump>')
        xml.append(f'  <range start="0x{start_addr:08X}" end="0x{end_addr:08X}"/>')
        xml.append('  <data>')
        
        # Группировка по строкам по 16 байт
        for addr in range(start_addr, end_addr, 16):
            line_end = min(addr + 16, end_addr)
            hex_bytes = []
            ascii_chars = []
            
            for i in range(addr, line_end):
                byte = self.memory[i]
                hex_bytes.append(f'{byte:02X}')
                ascii_chars.append(chr(byte) if 32 <= byte < 127 else '.')
            
            hex_str = ' '.join(hex_bytes)
            ascii_str = ''.join(ascii_chars)
            xml.append(f'    <line addr="0x{addr:08X}">')
            xml.append(f'      <hex>{hex_str}</hex>')
            xml.append(f'      <ascii>{ascii_str}</ascii>')
            xml.append('    </line>')
        
        xml.append('  </data>')
        xml.append('  <stack>')
        for i, value in enumerate(reversed(self.stack)):
            xml.append(f'    <value index="{i}">0x{value:08X}</value>')
        xml.append('  </stack>')
        xml.append('</memory_dump>')
        
        return '\n'.join(xml)