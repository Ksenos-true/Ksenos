#!/usr/bin/env python3
"""
Тесты для парсера конфигурационного языка
"""

import unittest
import tempfile
import os
import sys
from io import StringIO

# Добавляем путь к текущей директории для импорта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_parser import parse_config, GRAMMAR, ConfigTransformer
from lark import Lark


class TestConfigParser(unittest.TestCase):
    """Тесты парсера конфигурационного языка"""
    
    def test_1_basic_dictionary(self):
        """Тест простого словаря"""
        input_text = """{
    name => [[Simple Config]],
    version => 1.0
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['name'], 'Simple Config')
        self.assertEqual(result['version'], 1.0)
    
    def test_2_numbers_format(self):
        """Тест формата чисел (обязательно с точкой)"""
        input_text = """{
    positive => 123.0,
    negative => -45.6,
    with_plus => +78.9
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['positive'], 123.0)
        self.assertEqual(result['negative'], -45.6)
        self.assertEqual(result['with_plus'], 78.9)
    
    def test_3_nested_dictionary(self):
        """Тест вложенных словарей"""
        input_text = """{
    user => {
        personal => {
            name => [[Alice]],
            age => 25.0
        },
        account => {
            id => 1001.0,
            active => true
        }
    }
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['user']['personal']['name'], 'Alice')
        self.assertEqual(result['user']['personal']['age'], 25.0)
        self.assertEqual(result['user']['account']['id'], 1001.0)
    
    def test_4_constants_declaration(self):
        """Тест объявления констант"""
        input_text = """var base_url [[http://example.com]]
var port 8080.0
var timeout 30.0

{
    server => {
        url => base_url,
        port => port,
        timeout => timeout
    }
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['server']['url'], 'http://example.com')
        self.assertEqual(result['server']['port'], 8080.0)
        self.assertEqual(result['server']['timeout'], 30.0)
    
    def test_5_constant_expressions(self):
        """Тест константных выражений"""
        input_text = """var x 10.0
var y 3.0

{
    addition => ?(x + y),
    subtraction => ?(x - y),
    complex => ?(x + y - 2.0)
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['addition'], 13.0)      # 10 + 3
        self.assertEqual(result['subtraction'], 7.0)    # 10 - 3
        self.assertEqual(result['complex'], 11.0)       # 10 + 3 - 2
    
    def test_6_chr_function(self):
        """Тест функции chr()"""
        input_text = """{
    letter_a => ?(chr(65.0)),
    digit_zero => ?(chr(48.0)),
    snowflake => ?(chr(10052.0))
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['letter_a'], 'A')
        self.assertEqual(result['digit_zero'], '0')
        self.assertEqual(result['snowflake'], '❄')
    
    def test_7_mod_function(self):
        """Тест функции mod()"""
        input_text = """{
    mod1 => ?(mod(10.0, 3.0)),
    mod2 => ?(mod(15.0, 4.0)),
    mod3 => ?(mod(7.0, 2.0))
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['mod1'], 1.0)   # 10 % 3
        self.assertEqual(result['mod2'], 3.0)   # 15 % 4
        self.assertEqual(result['mod3'], 1.0)   # 7 % 2
    
    def test_8_multiline_strings(self):
        """Тест многострочных строк"""
        input_text = """{
    poem => [[Roses are red,
Violets are blue,
Sugar is sweet,
And so are you.]],
    code => [[function test() {
    return 42;
}]]
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertIn('Roses are red', result['poem'])
        self.assertIn('function test()', result['code'])
    
    def test_9_comments(self):
        """Тест комментариев"""
        input_text = """-- Это основной конфигурационный файл
{
    -- Настройки приложения
    app_name => [[MyApp]],  -- название приложения
    version => 2.5,         -- версия
    -- Настройки базы данных
    db => {
        host => [[localhost]]  -- хост БД
    }
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['app_name'], 'MyApp')
        self.assertEqual(result['version'], 2.5)
        self.assertEqual(result['db']['host'], 'localhost')
    
    def test_10_error_undefined_constant(self):
        """Тест ошибки неопределенной константы"""
        input_text = """{
    result => ?(undefined_var + 5.0)
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        with self.assertRaises(ValueError) as ctx:
            parser.parse(input_text)
        self.assertIn('Неизвестная константа', str(ctx.exception))
    
    def test_11_error_mod_by_zero(self):
        """Тест ошибки деления на ноль в mod"""
        input_text = """{
    result => ?(mod(10.0, 0.0))
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        with self.assertRaises(ValueError) as ctx:
            parser.parse(input_text)
        self.assertIn('Деление на ноль', str(ctx.exception))
    
    def test_12_empty_dictionary(self):
        """Тест пустого словаря"""
        input_text = """{
    empty => {},
    non_empty => {
        key => [[value]]
    }
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['empty'], {})
        self.assertEqual(result['non_empty']['key'], 'value')
    
    def test_13_complex_nesting(self):
        """Тест сложной вложенности"""
        input_text = """var multiplier 2.0

{
    level1 => {
        level2 => {
            level3 => {
                value => 10.0,
                calculated => ?(multiplier * 10.0)
            }
        }
    }
}"""
        parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
        result = parser.parse(input_text)
        self.assertEqual(result['level1']['level2']['level3']['value'], 10.0)
        self.assertEqual(result['level1']['level2']['level3']['calculated'], 20.0)


class TestCommandLine(unittest.TestCase):
    """Тесты командной строки"""
    
    def test_cli_parsing(self):
        """Тест работы через командную строку"""
        import subprocess
        import tempfile
        
        # Создаем временный входной файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""{
    test => [[CLI Test]],
    value => 42.0
}""")
            input_file = f.name
        
        # Создаем временный выходной файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            output_file = f.name
        
        try:
            # Запускаем парсер
            with open(input_file, 'r') as infile:
                result = subprocess.run(
                    [sys.executable, 'config_parser.py', '-o', output_file],
                    stdin=infile,
                    capture_output=True,
                    text=True
                )
            
            # Проверяем успешное выполнение
            self.assertEqual(result.returncode, 0)
            
            # Проверяем содержимое выходного файла
            with open(output_file, 'r') as f:
                content = f.read()
                self.assertIn('test: CLI Test', content)
                self.assertIn('value: 42.0', content)
        
        finally:
            # Удаляем временные файлы
            if os.path.exists(input_file):
                os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


def run_examples():
    """Запуск и демонстрация примеров"""
    examples = [
        ("Пример 1: Веб-сервер", """{
    server => {
        name => [[Nginx Web Server]],
        port => 8080.0,
        workers => 4.0,
        settings => {
            gzip => true,
            cache => 3600.0
        }
    }
}"""),
        
        ("Пример 2: Игровой персонаж", """var base_health 100.0
var level 5.0

{
    character => {
        name => [[Dragon Slayer]],
        class => [[Warrior]],
        health => ?(base_health + level * 20.0),
        attack => 25.5,
        defense => 15.0,
        symbol => ?(chr(9876.0))
    }
}"""),
        
        ("Пример 3: Научный эксперимент", """var pi 3.14159
var measurements 1000.0

{
    experiment => {
        title => [[Optics Study]],
        researcher => [[Dr. Smith]],
        parameters => {
            wavelength => 632.8,
            angle => 45.0,
            samples => measurements
        },
        result_symbol => ?(chr(9633.0))
    }
}""")
    ]
    
    print("\n" + "="*60)
    print("ДЕМОНСТРАЦИЯ ПРИМЕРОВ КОНФИГУРАЦИЙ")
    print("="*60)
    
    for i, (name, config) in enumerate(examples, 1):
        print(f"\n{'='*40}")
        print(f"ПРИМЕР {i}: {name}")
        print(f"{'='*40}")
        print("Входные данные:")
        print(config)
        
        try:
            parser = Lark(GRAMMAR, parser='lalr', transformer=ConfigTransformer())
            result = parser.parse(config)
            print(f"\nРезультат парсинга (Python-объект):")
            print(result)
            
            # Показываем как будет выглядеть YAML
            import yaml
            yaml_output = yaml.dump(result, allow_unicode=True, default_flow_style=False)
            print(f"\nБудет преобразовано в YAML:")
            print(yaml_output)
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")


if __name__ == '__main__':
    print("Запуск тестов парсера конфигурационного языка...")
    print("Вариант 19")
    
    # Запуск тестов
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfigParser)
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite)
    
    # Демонстрация примеров
    if test_result.wasSuccessful():
        run_examples()
    
    # Запуск тестов командной строки
    print("\n" + "="*60)
    print("ТЕСТЫ КОМАНДНОЙ СТРОКИ")
    print("="*60)
    cli_suite = unittest.TestLoader().loadTestsFromTestCase(TestCommandLine)
    cli_result = runner.run(cli_suite)
    
    print("\n" + "="*60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*60)
    print(f"Тесты парсера: {'✅ ПРОЙДЕНЫ' if test_result.wasSuccessful() else '❌ ЕСТЬ ОШИБКИ'}")
    print(f"Тесты CLI: {'✅ ПРОЙДЕНЫ' if cli_result.wasSuccessful() else '❌ ЕСТЬ ОШИБКИ'}")