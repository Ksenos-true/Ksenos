#!/usr/bin/env python3
"""
Тесты для ассемблера и интерпретатора УВМ
"""

import json
import tempfile
import os
import sys
from pathlib import Path
from assembler import Assembler
from interpreter import Interpreter

def test_specific_instructions():
    """Тестирование конкретных инструкций из спецификации"""
    print("Тест 1: Проверка кодирования инструкций из спецификации")
    print("-" * 60)
    
    assembler = Assembler()
    
    # Тест LOAD_CONST (A=43, B=45)
    instr = ('LOAD_CONST', 45)
    binary = assembler.encode_instruction(instr)
    expected = bytes([0xAB, 0x16, 0x00, 0x00])
    print(f"LOAD_CONST (45): {binary.hex(' ')}")
    print(f"Ожидается:       {expected.hex(' ')}")
    if binary != expected:
        print(f" Ошибка: LOAD_CONST кодируется неверно")
        return False
    
    # Тест READ_MEM (A=120, B=829)
    instr = ('READ_MEM', 829)
    binary = assembler.encode_instruction(instr)
    expected = bytes([0xF8, 0x9E, 0x01, 0x00])
    print(f"\nREAD_MEM (829):  {binary.hex(' ')}")
    print(f"Ожидается:       {expected.hex(' ')}")
    if binary != expected:
        print(f" Ошибка: READ_MEM кодируется неверно")
        return False
    
    # Тест WRITE_MEM (A=72)
    instr = ('WRITE_MEM',)
    binary = assembler.encode_instruction(instr)
    expected = bytes([0x48, 0x00, 0x00, 0x00])
    print(f"\nWRITE_MEM:       {binary.hex(' ')}")
    print(f"Ожидается:       {expected.hex(' ')}")
    if binary != expected:
        print(f" Ошибка: WRITE_MEM кодируется неверно")
        return False
    
    # Тест DIV (A=121, B=125)
    instr = ('DIV', 125)
    binary = assembler.encode_instruction(instr)
    expected = bytes([0xF9, 0x3E, 0x00, 0x00])
    print(f"\nDIV (125):       {binary.hex(' ')}")
    print(f"Ожидается:       {expected.hex(' ')}")
    if binary != expected:
        print(f" Ошибка: DIV кодируется неверно")
        return False
    
    print("\n" + "=" * 60)
    print(" Все инструкции кодируются правильно!")
    print("=" * 60)
    return True

def test_assembler_json():
    """Тестирование ассемблера с JSON входом"""
    print("\nТест 2: Тестирование ассемблера с JSON программой")
    print("-" * 60)
    
    # Создание тестовой программы
    test_program = [
        {"instruction": "LOAD_CONST", "operands": [100]},
        {"instruction": "LOAD_CONST", "operands": [200]},
        {"instruction": "WRITE_MEM", "operands": []},
        {"instruction": "LOAD_CONST", "operands": [300]},
        {"instruction": "READ_MEM", "operands": [50]},
        {"instruction": "DIV", "operands": [400]},
    ]
    
    # Сохранение во временный файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_program, f)
        json_file = f.name
    
    bin_file = None
    try:
        # Ассемблирование
        assembler = Assembler()
        
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
            bin_file = f.name
        
        # Запуск в тестовом режиме
        print("Запуск ассемблера в тестовом режиме...")
        assembler.assemble(json_file, bin_file, test_mode=True)
        
        # Проверка размера файла
        file_size = os.path.getsize(bin_file)
        expected_size = len(test_program) * 4
        print(f"\nРазмер бинарного файла: {file_size} байт (ожидается: {expected_size} байт)")
        
        if file_size != expected_size:
            print(f"❌ Ошибка: неверный размер бинарного файла")
            return False
        
        print(" Ассемблер работает корректно с JSON входом")
        return True
        
    finally:
        # Очистка временных файлов
        os.unlink(json_file)
        if bin_file and os.path.exists(bin_file):
            os.unlink(bin_file)

def test_interpreter_array_copy():
    """Тестирование интерпретатора: копирование массива"""
    print("\nТест 3: Тестирование интерпретатора - копирование массива")
    print("-" * 60)
    
    # Создание программы для копирования массива
    copy_program = [
        # Инициализация исходного массива
        {"instruction": "LOAD_CONST", "operands": [0x12345678]},
        {"instruction": "LOAD_CONST", "operands": [100]},
        {"instruction": "WRITE_MEM", "operands": []},
        
        {"instruction": "LOAD_CONST", "operands": [0x87654321]},
        {"instruction": "LOAD_CONST", "operands": [104]},
        {"instruction": "WRITE_MEM", "operands": []},
        
        {"instruction": "LOAD_CONST", "operands": [0xABCDEF12]},
        {"instruction": "LOAD_CONST", "operands": [108]},
        {"instruction": "WRITE_MEM", "operands": []},
        
        # Копирование массива из адреса 100 в адрес 200
        # Первый элемент
        {"instruction": "LOAD_CONST", "operands": [100]},
        {"instruction": "READ_MEM", "operands": [0]},
        {"instruction": "LOAD_CONST", "operands": [200]},
        {"instruction": "WRITE_MEM", "operands": []},
        
        # Второй элемент
        {"instruction": "LOAD_CONST", "operands": [104]},
        {"instruction": "READ_MEM", "operands": [0]},
        {"instruction": "LOAD_CONST", "operands": [204]},
        {"instruction": "WRITE_MEM", "operands": []},
        
        # Третий элемент
        {"instruction": "LOAD_CONST", "operands": [108]},
        {"instruction": "READ_MEM", "operands": [0]},
        {"instruction": "LOAD_CONST", "operands": [208]},
        {"instruction": "WRITE_MEM", "operands": []},
    ]
    
    # Сохранение программы
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(copy_program, f)
        json_file = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
        bin_file = f.name
    
    try:
        # Ассемблирование
        assembler = Assembler()
        assembler.assemble(json_file, bin_file)
        
        # Запуск интерпретатора
        print("Запуск интерпретатора для копирования массива...")
        interpreter = Interpreter()
        interpreter.run(bin_file)
        
        # Проверка результатов
        # Создаем отдельный экземпляр для проверки памяти
        test_interpreter = Interpreter()
        test_interpreter.load_program(bin_file)
        
        # Проверяем исходные значения
        val1 = test_interpreter.memory.read_word(100)
        val2 = test_interpreter.memory.read_word(104)
        val3 = test_interpreter.memory.read_word(108)
        
        # Проверяем скопированные значения
        copy1 = test_interpreter.memory.read_word(200)
        copy2 = test_interpreter.memory.read_word(204)
        copy3 = test_interpreter.memory.read_word(208)
        
        print(f"\nИсходный массив: [{hex(val1)}, {hex(val2)}, {hex(val3)}]")
        print(f"Скопированный массив: [{hex(copy1)}, {hex(copy2)}, {hex(copy3)}]")
        
        if val1 != copy1:
            print(f" Первое значение скопировано неверно")
            return False
        if val2 != copy2:
            print(f" Второе значение скопировано неверно")
            return False
        if val3 != copy3:
            print(f" Третье значение скопировано неверно")
            return False
        
        print(" Копирование массива выполнено успешно!")
        return True
        
    finally:
        # Очистка временных файлов
        os.unlink(json_file)
        if os.path.exists(bin_file):
            os.unlink(bin_file)

def test_division():
    """Тестирование команды деления"""
    print("\nТест 4: Тестирование команды DIV")
    print("-" * 60)
    
    # Создание программы для тестирования деления
    div_program = [
        # Загрузка делимого (100) на стек
        {"instruction": "LOAD_CONST", "operands": [100]},
        
        # Запись делителя (25) в память по адресу 500
        {"instruction": "LOAD_CONST", "operands": [25]},
        {"instruction": "LOAD_CONST", "operands": [500]},
        {"instruction": "WRITE_MEM", "operands": []},
        
        # Выполнение деления 100 / 25
        {"instruction": "DIV", "operands": [500]},
        
        # Запись результата в память по адресу 600
        {"instruction": "LOAD_CONST", "operands": [600]},
        {"instruction": "WRITE_MEM", "operands": []},
    ]
    
    # Сохранение программы
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(div_program, f)
        json_file = f.name
    
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
        bin_file = f.name
    
    try:
        # Ассемблирование
        assembler = Assembler()
        assembler.assemble(json_file, bin_file)
        
        # Запуск интерпретатора
        print("Запуск интерпретатора для тестирования деления...")
        interpreter = Interpreter()
        interpreter.run(bin_file)
        
        # Проверка результата
        test_interpreter = Interpreter()
        test_interpreter.load_program(bin_file)
        
        divisor = test_interpreter.memory.read_word(500)
        result = test_interpreter.memory.read_word(600)
        
        print(f"\nДелитель в памяти: {divisor}")
        print(f"Результат деления (100 / 25): {result}")
        
        if divisor != 25:
            print(f" Делитель записан неверно")
            return False
        if result != 4:
            print(f" Результат деления неверен (100 / 25 = 4)")
            return False
        
        print(" Деление выполнено успешно!")
        return True
        
    finally:
        # Очистка временных файлов
        os.unlink(json_file)
        if os.path.exists(bin_file):
            os.unlink(bin_file)

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ ДЛЯ АССЕМБЛЕРА И ИНТЕРПРЕТАТОРА УВМ")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        # Тест 1
        if test_specific_instructions():
            tests_passed += 1
        
        # Тест 2
        if test_assembler_json():
            tests_passed += 1
        
        # Тест 3
        if test_interpreter_array_copy():
            tests_passed += 1
        
        # Тест 4
        if test_division():
            tests_passed += 1
        
        print("\n" + "=" * 70)
        print(f"ИТОГ: {tests_passed}/{total_tests} тестов пройдено")
        
        if tests_passed == total_tests:
            print(" ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            return True
        else:
            print(f"НЕ ВСЕ ТЕСТЫ ПРОЙДЕНЫ: {total_tests - tests_passed} тестов не пройдено")
            return False
        
    except Exception as e:
        print(f"\n Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)