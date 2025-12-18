#!/usr/bin/env python3


import sys
import argparse
import yaml
from typing import Any, Dict
import lark

# Грамматика учебного конфигурационного языка
GRAMMAR = r"""
start: (var_decl | dict_decl | COMMENT)*

var_decl: "var" NAME value
dict_decl: NAME "=>" value

value: number
     | string
     | dict
     | const_expr
     | BOOL

dict: "{" [dict_item ("," dict_item)*] "}"
dict_item: NAME "=>" value

const_expr: "?(" expr ")"
expr: term (("+" | "-") term)*
term: factor (("*" | "/") factor)*
factor: atom
atom: NAME -> var_ref
    | number
    | function_call
    | "(" expr ")"

function_call: "chr(" expr ")" -> chr_func
             | "mod(" expr "," expr ")" -> mod_func

string: STRING
number: FLOAT | INT
BOOL: "true" | "false"
NAME: /[a-zA-Z][_a-zA-Z0-9]*/

STRING: /\[\[[^\]]*\]\]/
FLOAT: /[+-]?\d+\.\d+/
INT: /[+-]?\d+/

COMMENT: /--[^\n]*/
%ignore COMMENT
%ignore /[ \t\r\n\f]+/
"""

class ConfigTransformer(lark.Transformer):
    """Трансформер для преобразования AST в Python-структуры"""
    
    def __init__(self):
        super().__init__()
        self.variables = {}
        self.result = {}
    
    def NAME(self, token):
        return str(token)
    
    def INT(self, token):
        return int(token.value)
    
    def FLOAT(self, token):
        return float(token.value)
    
    def number(self, tokens):
        return tokens[0]
    
    def BOOL(self, token):
        return token.value == "true"
    
    def STRING(self, token):
        # Убираем [[ и ]] со скобок
        s = str(token.value)
        return s[2:-2]
    
    def string(self, tokens):
        return tokens[0]
    
    def var_decl(self, children):
        name, value = children
        self.variables[name] = value
        return None  # Не добавляем в результат
    
    def dict_decl(self, children):
        name, value = children
        self.result[name] = value
        return None
    
    def dict(self, children):
        if children:
            return dict(children)
        return {}
    
    def dict_item(self, children):
        name, value = children
        return (name, value)
    
    def const_expr(self, children):
        return children[0]
    
    def expr(self, children):
        result = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            if op == '+':
                result = result + right
            elif op == '-':
                result = result - right
            i += 2
        return result
    
    def term(self, children):
        result = children[0]
        i = 1
        while i < len(children):
            op = children[i]
            right = children[i + 1]
            if op == '*':
                result = result * right
            elif op == '/':
                result = result / right
            i += 2
        return result
    
    def var_ref(self, children):
        name = children[0]
        if name not in self.variables:
            raise ValueError(f"Неопределенная переменная: {name}")
        return self.variables[name]
    
    def chr_func(self, children):
        value = children[0]
        if isinstance(value, (int, float)):
            return chr(int(value))
        raise ValueError(f"Ожидалось число для chr(), получено: {type(value)}")
    
    def mod_func(self, children):
        a, b = children
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return float(a) % float(b)
        raise ValueError("Ожидались числа для mod()")
    
    def start(self, children):
        # Возвращаем собранный результат
        return self.result

def parse_input(input_text: str) -> Dict[str, Any]:
    """Парсит входной текст и возвращает структуру данных"""
    try:
        parser = lark.Lark(GRAMMAR, parser='lalr')
        tree = parser.parse(input_text)
        transformer = ConfigTransformer()
        result = transformer.transform(tree)
        return result
    except lark.exceptions.LarkError as e:
        # Более понятное сообщение об ошибке
        context = str(e).split('\n')[0]
        raise ValueError(f"Синтаксическая ошибка: {context}")

def convert_to_yaml(data: Dict[str, Any]) -> str:
    """Конвертирует данные в YAML формат"""
    return yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

def main():
    parser = argparse.ArgumentParser(
        description='Преобразователь учебного конфигурационного языка в YAML',
        prog='dzPolezhaeva19.py'
    )
    parser.add_argument(
        '-o', '--output',
        required=True,
        help='Путь к выходному YAML файлу'
    )
    
    args = parser.parse_args()
    
    try:
        # Чтение из стандартного ввода
        input_text = sys.stdin.read()
        
        if not input_text.strip():
            print("Ошибка: входной текст пуст", file=sys.stderr)
            sys.exit(1)
        
        # Парсинг входных данных
        data = parse_input(input_text)
        
        # Конвертация в YAML
        yaml_output = convert_to_yaml(data)
        
        # Запись в файл
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(yaml_output)
        
        print(f"Успешно преобразовано. Результат записан в {args.output}")
        return 0
        
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(1)

def run_examples():
    """Запуск примеров из разных предметных областей"""
    
    print("=" * 70)
    print("ПРЕОБРАЗОВАТЕЛЬ КОНФИГУРАЦИОННОГО ЯЗЫКА В YAML")
    print("Вариант №19 | Файл: dzPolezhaeva19.py")
    print("=" * 70)
    
    # Пример 1: Конфигурация веб-сервера
    print("\n" + "=" * 70)
    print("ПРИМЕР 1: КОНФИГУРАЦИЯ ВЕБ-СЕРВЕРА")
    print("=" * 70)
    
    web_config = """-- Конфигурация веб-сервера
var port 8080.0
var timeout 30.0

server {
    host => [[localhost]],
    port => ?(port + 1.0),
    timeout => timeout,
    ssl => {
        enabled => true,
        cert_path => [[/etc/ssl/cert.pem]]
    },
    logging => {
        level => [[debug]],
        file => [[/var/log/server.log]]
    }
}"""
    
    print("Входные данные (конфигурационный язык):")
    print("-" * 40)
    print(web_config)
    
    print("\nРезультат (YAML):")
    print("-" * 40)
    try:
        result = parse_input(web_config)
        yaml_output = convert_to_yaml(result)
        print(yaml_output)
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
    
    # Пример 2: Конфигурация игры
    print("\n" + "=" * 70)
    print("ПРИМЕР 2: КОНФИГУРАЦИЯ ИГРЫ")
    print("=" * 70)
    
    game_config = """-- Конфигурация параметров игры
var base_health 100.0
var difficulty 2.0

game {
    player => {
        health => ?(base_health * difficulty),
        speed => 5.5,
        inventory_size => 20.0,
        abilities => [[fireball,shield,heal]]
    },
    world => {
        size => 1000.0,
        gravity => 9.8,
        weather_enabled => true
    },
    graphics => {
        resolution => [[1920x1080]],
        vsync => false,
        texture_quality => [[high]]
    }
}"""
    
    print("Входные данные (конфигурационный язык):")
    print("-" * 40)
    print(game_config)
    
    print("\nРезультат (YAML):")
    print("-" * 40)
    try:
        result = parse_input(game_config)
        yaml_output = convert_to_yaml(result)
        print(yaml_output)
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
    
    # Пример 3: Конфигурация базы данных
    print("\n" + "=" * 70)
    print("ПРИМЕР 3: КОНФИГУРАЦИЯ БАЗЫ ДАННЫХ")
    print("=" * 70)
    
    db_config = """-- Конфигурация подключения к базе данных
var default_port 5432.0
var multiplier 2.0

database {
    connection => {
        host => [[127.0.0.1]],
        port => ?(mod(default_port, 1000.0) + 3306.0),
        user => [[admin_user]],
        password => [[secure_pass123]]
    },
    settings => {
        pool_size => ?(10.0 * multiplier),
        timeout => 60.0,
        ssl_enabled => true,
        encoding => [[UTF-8]]
    },
    tables => {
        users => [[id,name,email,created_at]],
        products => [[id,title,price,quantity]]
    }
}"""
    
    print("Входные данные (конфигурационный язык):")
    print("-" * 40)
    print(db_config)
    
    print("\nРезультат (YAML):")
    print("-" * 40)
    try:
        result = parse_input(db_config)
        yaml_output = convert_to_yaml(result)
        print(yaml_output)
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
    
    # Пример 4: Демонстрация функции chr()
    print("\n" + "=" * 70)
    print("ПРИМЕР 4: ИСПОЛЬЗОВАНИЕ ФУНКЦИИ chr()")
    print("=" * 70)
    
    chr_example = """-- Пример использования функции chr()
var ascii_a 65.0
var ascii_b 66.0

characters {
    letter_a => ?(chr(ascii_a)),
    letter_b => ?(chr(ascii_b)),
    sum_chars => ?(chr(ascii_a + ascii_b - 65.0))
}"""
    
    print("Входные данные (конфигурационный язык):")
    print("-" * 40)
    print(chr_example)
    
    print("\nРезультат (YAML):")
    print("-" * 40)
    try:
        result = parse_input(chr_example)
        yaml_output = convert_to_yaml(result)
        print(yaml_output)
    except Exception as e:
        print(f"Ошибка при обработке: {e}")
    
    print("\n" + "=" * 70)
    print("ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ:")
    print("=" * 70)
    print("1. Сохраните конфигурацию в файл (например, config.txt)")
    print("2. Запустите преобразование:")
    print("   python dzPolezhaeva19.py -o output.yaml < config.txt")
    print("\nИли используйте прямое перенаправление:")
    print('   echo "app { name => [[Test]] }" | python dzPolezhaeva19.py -o out.yaml')
    print("\nДля запуска обработки введите:")
    print("   python dzPolezhaeva19.py -o результат.yaml")
    print("   (затем введите конфигурацию и нажмите Ctrl+D для завершения ввода)")

def test_parser():
    """Тестирование парсера"""
    print("\n" + "=" * 70)
    print("ТЕСТИРОВАНИЕ ПАРСЕРА")
    print("=" * 70)
    
    tests = [
        ("Тест 1: Простой словарь", """
config {
    name => [[test]],
    value => 42.0
}"""),
        
        ("Тест 2: Переменные и выражения", """
var x 10.0
var y 3.0

result {
    sum => ?(x + y),
    product => ?(x * y),
    remainder => ?(mod(x, y))
}"""),
        
        ("Тест 3: Вложенные структуры", """
system {
    network => {
        ip => [[192.168.1.1]],
        mask => [[255.255.255.0]]
    },
    services => {
        ssh => {
            port => 22.0,
            enabled => true
        }
    }
}"""),
        
        ("Тест 4: Ошибка (неопределенная переменная)", """
var a 5.0

error_test {
    value => ?(b + 10.0)  -- b не определена
}"""),
        
        ("Тест 5: Комментарии", """
-- Главная конфигурация
app {
    -- Настройки сети
    network => {
        host => [[localhost]],  -- хост для подключения
        port => 8080.0
    },
    
    -- Настройки безопасности
    security => {
        ssl => true  -- использовать SSL
    }
}"""),
    ]
    
    for test_name, test_input in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        print("Ввод:", test_input.strip().replace('\n', '\\n'))
        try:
            result = parse_input(test_input)
            yaml_output = convert_to_yaml(result)
            print("✓ Успешно")
            print("Результат:", yaml_output.strip())
        except Exception as e:
            print(f"✗ Ошибка: {e}")

if __name__ == "__main__":
    # Запуск примеров при прямом запуске скрипта
    run_examples()
    
    # Запуск тестов
    test_parser()
    
    # Вывод инструкции для использования как CLI инструмента
    print("\n" + "=" * 70)
    print("ДЛЯ ИСПОЛЬЗОВАНИЯ КАК ИНСТРУМЕНТА КОМАНДНОЙ СТРОКИ:")
    print("=" * 70)
    print("Раскомментируйте строку 'main()' в конце файла")
    print("и используйте:")
    print("  python dzPolezhaeva19.py -o config.yaml < input.txt")
    
    # Для использования как CLI инструмента, раскомментируйте следующую строку:
    # main()